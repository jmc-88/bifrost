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

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject  # isort:skip


def _gtk_widget_set_margin(widget: Gtk.Widget, margin: int) -> None:
    """Sets all widget margins to the same value."""
    widget.set_margin_start(margin)
    widget.set_margin_top(margin)
    widget.set_margin_end(margin)
    widget.set_margin_bottom(margin)


Gtk.Widget.set_margin = _gtk_widget_set_margin


def _gtk_widget_set_align(widget: Gtk.Widget, align: Gtk.Align) -> None:
    """Sets horizontal and vertical 'align' to the same value."""
    widget.set_halign(align)
    widget.set_valign(align)


Gtk.Widget.set_align = _gtk_widget_set_align


def _gtk_widget_set_expand(widget: Gtk.Widget, expand: bool) -> None:
    """Sets horizontal and vertical 'expand' to the same value."""
    widget.set_hexpand(expand)
    widget.set_vexpand(expand)


Gtk.Widget.set_expand = _gtk_widget_set_expand


def _gtk_button_set_label_with_mnemonic(button: Gtk.Button, label: str) -> None:
    """Sets a label with a mnemonic for the button."""
    button.set_use_underline(True)
    button.set_label(label)


Gtk.Button.set_label_with_mnemonic = _gtk_button_set_label_with_mnemonic


def _gtk_accel_group_connect_and_parse(
    accel_group: Gtk.AccelGroup, accelerator: str, closure: GObject.Closure
) -> None:
    """Connects the given accelerator to the given GObject.Closure."""
    key, mod = Gtk.accelerator_parse(accelerator)
    accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, closure)


Gtk.AccelGroup.connect_and_parse = _gtk_accel_group_connect_and_parse
