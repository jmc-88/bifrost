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

import gi
import wormhole

from . import widgets

gi.require_version("Gtk", "3.0")
gi.require_version("Granite", "1.0")
from gi.repository import Gdk, Gtk, GLib, GObject, Granite  # isort:skip

log = logging.getLogger(__name__)


class WelcomeView(Gtk.Box):
    """Page that will be shown at application startup time."""

    def __init__(self):
        super().__init__()

        GObject.signal_new(
            "send-clicked", self, GObject.SignalFlags.ACTION, GObject.TYPE_NONE, ()
        )
        GObject.signal_new(
            "receive-clicked", self, GObject.SignalFlags.ACTION, GObject.TYPE_NONE, ()
        )
        GObject.signal_new(
            "downloads-clicked", self, GObject.SignalFlags.ACTION, GObject.TYPE_NONE, ()
        )

        welcome = Granite.WidgetsWelcome.new(
            "Welcome to Bifrost", "What would you like to do?"
        )
        welcome.get_style_context().remove_class(Gtk.STYLE_CLASS_VIEW)
        self.add(welcome)

        send_index = welcome.append(
            "document-export", "Send Files", "Upload data to another computer"
        )
        receive_index = welcome.append(
            "document-import", "Receive Files", "Download data from another computer"
        )
        downloads_index = welcome.append(
            "folder", "Show Downloads", "Open your Downloads folder"
        )

        def _activated(_, index):
            if index == send_index:
                self.emit("send-clicked")
                return

            if index == receive_index:
                self.emit("receive-clicked")
                return

            if index == downloads_index:
                self.emit("downloads-clicked")
                return

        welcome.connect("activated", _activated)


class SendView(Gtk.EventBox, Gtk.Widget):
    """Page that will be shown when selecting what to send."""

    def __init__(self):
        super().__init__()

        GObject.signal_new(
            "files-chosen",
            self,
            GObject.SignalFlags.ACTION,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,),
        )

        drop = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        drop.set_expand(True)
        # drop.get_style_context ().add_class ("drop")
        self.add(drop)

        title = Gtk.Label.new("Drag files and folders here")
        title.get_style_context().add_class("h2")
        title.set_expand(True)
        title.set_valign(Gtk.Align.END)
        drop.add(title)

        subtitle = Gtk.Label.new("Or click to select a file")
        subtitle.get_style_context().add_class("h3")
        subtitle.set_opacity(0.5)
        subtitle.set_expand(True)
        subtitle.set_valign(Gtk.Align.START)
        drop.add(subtitle)

        self.drag_dest_set(
            Gtk.DestDefaults.ALL,
            [Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags.OTHER_APP, 0)],
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        self.connect("drag_motion", lambda _1, _2, _3, _4, _5: None)
        self.connect("drag_leave", lambda _1, _2, _3: None)
        self.connect("drag_data_received", self.on_drag_data_received)

    def do_button_press_event(self, event):
        del event  # unused

        chooser = Gtk.FileChooserDialog(
            "Select files or directories",
            self.get_toplevel(),
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                "_Upload",
                Gtk.ResponseType.ACCEPT,
            ),
        )
        chooser.set_default_response(Gtk.ResponseType.ACCEPT)
        chooser.set_select_multiple(True)

        filter_ = Gtk.FileFilter()
        filter_.set_name("Any file or directory")
        filter_.add_pattern("*")
        chooser.set_filter(filter_)

        if chooser.run() == Gtk.ResponseType.ACCEPT:
            paths = [GLib.filename_from_uri(u)[0] for u in chooser.get_uris()]
            self.emit("files-chosen", paths)

        chooser.close()

    def on_drag_data_received(
        self,
        widget: Gtk.Widget,
        context: Gdk.DragContext,
        x: int,
        y: int,
        data: Gtk.SelectionData,
        info: int,
        time: int,
    ):
        if data.get_length() < 0:
            log.warning("Empty data received, ignoring")
            Gtk.drag_finish(context, False, False, time)

        paths = [GLib.filename_from_uri(u)[0] for u in data.get_uris()]
        self.emit("files-chosen", paths)
        Gtk.drag_finish(context, True, False, time)


class ReceiveView(Gtk.EventBox):
    """Page that will be shown when choosing to receive files."""

    def __init__(self, wormhole: wormhole.wormhole):
        super().__init__()

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.set_expand(True)
        self.add(box)

        code_entry = widgets.CodeEntry(wormhole)
        code_entry.set_hexpand(True)
        box.add(code_entry)
