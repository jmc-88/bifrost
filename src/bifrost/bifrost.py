#!/usr/bin/python3
"""
Copyright (c) 2019 Daniele Cocca
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted (subject to the limitations in the
disclaimer below) provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

  * Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE
GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT
HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging
import os
import sys
from typing import List, Text

import gi
import wormhole
import wormhole.cli.public_relay

from . import views, widgets

from twisted.internet import defer, task, gtk3reactor  # isort:skip

gtk3reactor.install()

from twisted.internet import reactor  # isort:skip

gi.require_version("Gtk", "3.0")
gi.require_version("Granite", "1.0")
from gi.repository import Gio, Gdk, Gtk, GObject, GLib, Granite  # isort:skip


APPLICATION_ID = r"com.github.jmc-88.bifrost"
log = logging.getLogger(__name__)


def _ShowDownloads(_):
    """Opens $XDG_DOWNLOAD_DIR with the default file manager."""

    download_dir_uri = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOWNLOAD)
    if not download_dir_uri:
        log.error("Couldn't find a value for $XDG_DOWNLOAD_DIR")
        return

    if not Gio.AppInfo.launch_default_for_uri(f"file://{download_dir_uri}"):
        log.error('Couldn\'t open "%s"', download_dir_uri)
        return


class MainWindow(Gtk.ApplicationWindow, Gtk.Widget):
    def __init__(self, wormhole, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(400, 400)
        self.set_deletable(True)
        self.set_resizable(False)
        self.get_style_context().add_class("rainbow")
        self.get_style_context().add_class("rounded")

        accel_group = Gtk.AccelGroup.new()
        accel_group.connect_and_parse(
            "<Control>q", lambda _1, _2, _3, _4: (self.destroy(), True)
        )
        self.add_accel_group(accel_group)

        self.back_button = Gtk.Button.new_with_label("Back")
        self.back_button.get_style_context().add_class(Granite.STYLE_CLASS_BACK_BUTTON)
        self.back_button.connect("clicked", lambda _: self.show_child("welcome"))

        self.spinner = Gtk.Spinner.new()
        self.spinner.start()

        headerbar = Gtk.HeaderBar.new()
        headerbar.get_style_context().add_class("rainbow")
        headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)
        headerbar.set_show_close_button(True)
        headerbar.set_title("Bifrost")
        headerbar.pack_start(self.back_button)
        headerbar.pack_end(self.spinner)
        self.set_titlebar(headerbar)

        self.stack = widgets.StackWithBulletIcons()
        self.stack.set_border_width(10)
        self.stack.set_expand(True)
        self.stack.set_align(Gtk.Align.FILL)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        app = self.props.application
        welcome = views.WelcomeView()
        welcome.connect("send-clicked", lambda _: self.show_child("send"))
        welcome.connect("receive-clicked", lambda _: self.show_child("receive"))
        welcome.connect("downloads-clicked", _ShowDownloads)
        self.stack.add_named(welcome, "welcome")

        send = views.SendView()
        send.connect("files-chosen", self.on_files_chosen)
        self.stack.add_named(send, "send")

        receive = views.ReceiveView(wormhole)
        self.stack.add_named(receive, "receive")

        vbox = Gtk.VBox.new(False, 0)
        vbox.add(self.stack)
        vbox.add(widgets.AdvancedSettingsPane.new(app))
        self.add(vbox)

    def do_destroy(self):
        reactor.stop()

    def show_child(self, child_name):
        self.stack.set_visible_child_name(child_name)
        self.update_visibility()

    def update_visibility(self):
        self.spinner.hide()

        if self.stack.get_visible_child_name() == "welcome":
            self.back_button.hide()
        else:
            self.back_button.show()

    def show_all(self):
        super().show_all()
        self.update_visibility()

    @defer.inlineCallbacks
    def on_files_chosen(self, widget: Gtk.Widget, paths: List[Text]):
        w = self.get_application().wormhole
        welcome = yield w.get_welcome()
        if "motd" in welcome:
            log.info(f"MOTD: {welcome['motd']}")

        w.allocate_code()
        code = yield w.get_code()
        log.info(f"Wormhole code is: {code}")

        # TODO: show code in UI


class Bifrost(Gtk.Application, Gio.Application):
    def __init__(self, argv0):
        super().__init__(
            application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        resources = Gio.Resource.load(_resources_filename(argv0))
        if not resources:
            raise RuntimeError("can't load resources file from")
        Gio.resources_register(resources)

        self._application_id = APPLICATION_ID
        self._rendezvous_relay = wormhole.cli.public_relay.RENDEZVOUS_RELAY
        self._transit_relay = wormhole.cli.public_relay.TRANSIT_RELAY
        self.initialize_wormhole()

    @property
    def application_id(self):
        return self._application_id

    @application_id.setter
    def application_id(self, value: str):
        self._application_id = value
        self.initialize_wormhole()

    @property
    def rendezvous_relay(self):
        return self._rendezvous_relay

    @rendezvous_relay.setter
    def rendezvous_relay(self, value: str):
        self._rendezvous_relay = value
        self.initialize_wormhole()

    @property
    def transit_relay(self):
        return self._transit_relay

    @transit_relay.setter
    def transit_relay(self, value: str):
        self._transit_relay = value
        self.initialize_wormhole()

    def do_activate(self):
        win = MainWindow(self.wormhole, application=self, title="Bifrost")
        win.show_all()

        css_provider = Gtk.CssProvider.new()
        css_provider.load_from_resource("com/github/jmc-88/bifrost/application.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def initialize_wormhole(self):
        self.wormhole = wormhole.create(
            self.application_id, self.rendezvous_relay, reactor
        )


def _resources_filename(argv0):
    path = os.environ.get("_DEBUG_RESOURCE_PATH")
    if path:
        return os.path.abspath(path)

    return os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.dirname(argv0)),
            "share",
            APPLICATION_ID,
            f"{APPLICATION_ID}.gresource",
        )
    )


def main():
    app = Bifrost(sys.argv[0])
    reactor.registerGApplication(app)
    reactor.run()
