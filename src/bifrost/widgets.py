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

from . import bifrost

from typing import Callable, Text
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject  # isort:skip


class EntryWithValidation(Gtk.Entry):
    """Gtk.Entry with a custom text validation callback."""

    def __init__(self, validator: Callable[[Text], Text], *args, **kwargs):
        super().__init__()
        self.validate_text = validator

    def do_insert_text(self, new_text, new_text_length, position):
        del new_text_length  # unused

        new_text = self.validate_text(new_text)
        if not new_text:
            GObject.signal_stop_emission_by_name(self, "insert-text")
            return position

        new_length = len(new_text)
        self.get_buffer().insert_text(position, new_text, new_length)
        return position + new_length


class StackWithBulletIcons(Gtk.Stack):
    """Gtk.Stack which automatically sets 'icon-name' to 'pager-checked-symbolic'."""

    def add_named(self, child, *args, **kwargs):
        super().add_named(child, *args, **kwargs)
        self.child_set_property(child, "icon-name", "pager-checked-symbolic")

    def add_titled(self, child, *args, **kwargs):
        super().add_titled(child, *args, **kwargs)
        self.child_set_property(child, "icon-name", "pager-checked-symbolic")


class AdvancedSettingsPane(Gtk.Expander):
    """Collapsible pane for advanced application settings."""

    def __init__(self, application: "bifrost.Bifrost"):
        super().__init__()
        self.application = application

    @staticmethod
    def new(application: "bifrost.Bifrost"):
        pane = AdvancedSettingsPane(application)
        pane.set_margin(10)
        pane.set_label("Advanced settings")

        grid = Gtk.Grid.new()
        grid.set_margin(10)
        grid.set_margin_bottom(0)
        grid.set_column_spacing(10)
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(True)
        pane.add(grid)

        def _application_property_updater(property_name):
            def _update(editable):
                value = editable.get_text()
                if not value:
                    return
                setattr(application, property_name, value)

            return _update

        label = Gtk.Label.new("Application id:")
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry.new()
        entry.set_hexpand(True)
        entry.set_input_hints(Gtk.InputHints.NO_EMOJI)
        entry.set_text(application.application_id)
        entry.connect("changed", _application_property_updater("application_id"))
        grid.attach(label, 0, 0, 1, 1)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label.new("Rendezvous relay:")
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry.new()
        entry.set_hexpand(True)
        entry.set_input_hints(Gtk.InputHints.NO_EMOJI)
        entry.set_text(application.rendezvous_relay)
        entry.connect("changed", _application_property_updater("rendezvous_relay"))
        grid.attach(label, 0, 1, 1, 1)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label.new("Transit relay:")
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry.new()
        entry.set_hexpand(True)
        entry.set_input_hints(Gtk.InputHints.NO_EMOJI)
        entry.set_text(application.transit_relay)
        entry.connect("changed", _application_property_updater("transit_relay"))
        grid.attach(label, 0, 2, 1, 1)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, 1, 1)

        return pane
