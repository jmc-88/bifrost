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

import gi
import wormhole
import wormhole.cli.public_relay
from twisted.internet import defer, task

from . import views, widgets

gi.require_version("Gtk", "3.0")
gi.require_version("Granite", "1.0")
from gi.repository import Gio, Gdk, Gtk, GObject, GLib, Granite  # isort:skip


APPLICATION_ID = r"com.github.jmc-88.bifrost"
log = logging.getLogger(__name__)


class CodeEntry(widgets.EntryWithValidation):
    """Gtk.Entry for Magic Wormhole codes."""

    def __init__(self, wormhole: wormhole.wormhole, *args, **kwargs):
        def _input_validator(text):
            return "".join(c for c in text if not c.isspace())

        super().__init__(_input_validator, *args, **kwargs)

        completion = Gtk.EntryCompletion()
        completion.set_text_column(0)
        completion.set_popup_completion(False)
        completion.set_inline_completion(True)
        completion.set_inline_selection(True)
        self.set_completion(completion)

        self.model = Gtk.ListStore(str)
        completion.set_model(self.model)

        self.set_placeholder_text("Input Magic Wormhole code...")
        self.set_halign(Gtk.Align.CENTER)
        self.set_input_hints(
            Gtk.InputHints.NO_EMOJI
            | Gtk.InputHints.WORD_COMPLETION
            | Gtk.InputHints.LOWERCASE
        )


def _ShowDownloads(_):
    """Opens $XDG_DOWNLOAD_DIR with the default file manager."""

    download_dir_uri = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOWNLOAD)
    if not download_dir_uri:
        logging.error("Couldn't find a value for $XDG_DOWNLOAD_DIR")
        return

    if not Gio.AppInfo.launch_default_for_uri(f"file://{download_dir_uri}"):
        logging.error('Couldn\'t open "%s"', download_dir_uri)
        return


class MainWindow(Gtk.ApplicationWindow):
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

        settings_button = Gtk.Button.new_from_icon_name(
            "open-menu-symbolic", Gtk.IconSize.SMALL_TOOLBAR
        )
        settings_button.set_always_show_image(True)
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", lambda _: None)

        headerbar = Gtk.HeaderBar.new()
        headerbar.get_style_context().add_class("rainbow")
        headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)
        headerbar.set_show_close_button(True)
        headerbar.set_title("Bifrost")
        headerbar.pack_start(self.back_button)
        headerbar.pack_end(settings_button)
        headerbar.pack_end(self.spinner)
        self.set_titlebar(headerbar)

        self.stack = widgets.StackWithBulletIcons()
        self.stack.set_border_width(10)
        self.stack.set_expand(True)
        self.stack.set_align(Gtk.Align.FILL)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.add(self.stack)

        app = self.props.application
        welcome = views.WelcomeView()
        welcome.connect("send-clicked", lambda _: self.show_child("send"))
        welcome.connect("receive-clicked", _make_notifier(app, "Receive!"))
        welcome.connect("downloads-clicked", _ShowDownloads)
        self.stack.add_named(welcome, "welcome")

        send = views.SendView()
        send.connect("files-chosen", lambda _1, path: _make_notifier(app, path)(_1))
        self.stack.add_named(send, "send")

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


class Bifrost(Gtk.Application):
    def __init__(self, reactor, argv0):
        super().__init__(
            application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        resources = Gio.Resource.load(_resources_filename(argv0))
        if not resources:
            raise RuntimeError("can't load resources file from")
        Gio.resources_register(resources)

        self.wormhole = wormhole.create(
            APPLICATION_ID, wormhole.cli.public_relay.RENDEZVOUS_RELAY, reactor
        )

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


def _make_notifier(application, message, title="Mock", notification_id="mock"):
    def _notify(_):
        notification = Gio.Notification.new(title)
        notification.set_icon(Gio.ThemedIcon.new("dialog-information"))
        notification.set_body(message)
        application.send_notification(notification_id, notification)

    return _notify


def _resources_filename(argv0):
    path = os.environ.get("_DEBUG_RESOURCE_PATH")
    if path:
        return os.path.abspath(path)

    return os.path.abspath(
        path=os.path.join(
            os.path.dirname(os.path.dirname(argv0)),
            "share",
            APPLICATION_ID,
            f"{APPLICATION_ID}.gresource",
        )
    )


def _bifrost_main(reactor, argv=()):
    app = Bifrost(reactor, argv[0])
    rc = app.run(argv)
    if rc != 0:
        return defer.fail(
            rc
        )  # TODO: something better please, also check out SystemExit()
    return defer.succeed("ok")


def main():
    task.react(_bifrost_main, (sys.argv,))