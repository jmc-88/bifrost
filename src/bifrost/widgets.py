#!/usr/bin/python3
"""
Copyright 2019 Daniele Cocca (daniele.cocca@gmail.com)
"""

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
