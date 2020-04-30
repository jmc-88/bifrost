// Copyright (c) 2020 Daniele Cocca
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted (subject to the limitations in the
// disclaimer below) provided that the following conditions are met:
//
//   * Redistributions of source code must retain the above copyright
//     notice, this list of conditions and the following disclaimer.
//
//   * Redistributions in binary form must reproduce the above copyright
//     notice, this list of conditions and the following disclaimer in
//     the documentation and/or other materials provided with the
//     distribution.
//
//   * Neither the name of the copyright holder nor the names of its
//     contributors may be used to endorse or promote products derived
//     from this software without specific prior written permission.
//
// NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE
// GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT
// HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
// WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
// BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
// OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
// IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include <algorithm>
#include <iostream>
#include <iterator>

#include "views.hh"

WelcomeView::WelcomeView() {
  welcome = granite_widgets_welcome_new("Welcome to Bifrost",
                                        "What would you like to do?");
  granite_widgets_welcome_append(welcome, "document-export", "Send Files",
                                 "Upload data to another computer");
  gint receive_button_idx = granite_widgets_welcome_append(
      welcome, "document-import", "Receive Files",
      "Download data from another computer");
  granite_widgets_welcome_append(welcome, "folder", "Show Downloads",
                                 "Open your Downloads folder");

  // Mark "Receive Files" as yet to be implemented.
  granite_widgets_welcome_set_item_sensitivity(welcome, receive_button_idx,
                                               false);
  auto* receive_button = granite_widgets_welcome_get_button_from_index(
      welcome, receive_button_idx);
  gtk_widget_set_tooltip_text(GTK_WIDGET(receive_button),
                              "Not implemented yet");

  auto on_activated =
      +[](GraniteWidgetsWelcome* /*welcome*/, gint index, WelcomeView* self) {
        switch (index) {
          case 0 /* Send */:
            self->signal_send_selected.emit();
            break;

          case 1 /* Receive */:
            self->signal_receive_selected.emit();
            break;

          case 2 /* Downloads */:
            self->signal_downloads_selected.emit();
            break;
        }
      };
  g_signal_connect(welcome, "activated", G_CALLBACK(on_activated), this);

  auto welcome_widget = GTK_WIDGET(welcome);
  gtk_style_context_remove_class(gtk_widget_get_style_context(welcome_widget),
                                 GTK_STYLE_CLASS_VIEW);
  gtk_container_add(GTK_CONTAINER(gobj()), welcome_widget);
  gtk_widget_show_all(welcome_widget);
}

SendView::SendView() {
  drop.set_orientation(Gtk::Orientation::ORIENTATION_VERTICAL);
  drop.set_spacing(0);
  drop.set_hexpand(true);
  drop.set_vexpand(true);
  drop.show();
  add(drop);

  title.set_label("Drag files and folders here");
  title.get_style_context()->add_class("h2");
  title.set_hexpand(true);
  title.set_vexpand(true);
  title.set_valign(Gtk::Align::ALIGN_END);
  title.show();
  drop.add(title);

  subtitle.set_label("Or click to select a file");
  subtitle.get_style_context()->add_class("h3");
  subtitle.set_opacity(0.5);
  subtitle.set_hexpand(true);
  subtitle.set_vexpand(true);
  subtitle.set_valign(Gtk::Align::ALIGN_START);
  subtitle.show();
  drop.add(subtitle);

  drag_dest_set(
      {Gtk::TargetEntry("text/uri-list", Gtk::TargetFlags::TARGET_OTHER_APP)},
      Gtk::DestDefaults::DEST_DEFAULT_ALL,
      Gdk::DragAction::ACTION_COPY | Gdk::DragAction::ACTION_MOVE);
}

void SendView::process_chosen_files(
    const std::vector<Glib::ustring>& chosen_uris) {
  std::vector<std::string> filenames;
  std::transform(
      chosen_uris.cbegin(), chosen_uris.cend(), std::back_inserter(filenames),
      [](const Glib::ustring& uri) { return Glib::filename_from_uri(uri); });
  signal_files_chosen.emit(filenames);
}

void SendView::on_drag_data_received(
    const Glib::RefPtr<Gdk::DragContext>& context, int, int,
    const Gtk::SelectionData& selection_data, guint, guint time) {
  if (selection_data.get_length() < 0) {
    context->drag_finish(false, false, time);
    return;
  }

  process_chosen_files(selection_data.get_uris());
  context->drag_finish(true, false, time);
}

bool SendView::on_button_press_event(GdkEventButton* /*button_event*/) {
  auto chooser =
      Gtk::FileChooserDialog(dynamic_cast<Gtk::Window&>(*get_toplevel()),
                             "Select files or directories");
  chooser.add_button(Gtk::Stock::CANCEL, Gtk::ResponseType::RESPONSE_CANCEL);
  chooser.add_button("_Upload", Gtk::ResponseType::RESPONSE_ACCEPT);
  chooser.set_default_response(Gtk::ResponseType::RESPONSE_ACCEPT);
  chooser.set_select_multiple(true);

  auto filter = Gtk::FileFilter::create();
  filter->set_name("Any file or directory");
  filter->add_pattern("*");
  chooser.set_filter(filter);

  if (chooser.run() == Gtk::ResponseType::RESPONSE_ACCEPT)
    process_chosen_files(chooser.get_uris());

  chooser.close();
  return true;
}

SendCodeView::SendCodeView() {
  box.set_orientation(Gtk::Orientation::ORIENTATION_VERTICAL);
  box.set_spacing(0);
  box.set_hexpand(true);
  box.set_vexpand(true);
  box.show();
  add(box);

  title.set_label("The wormhole code is");
  title.get_style_context()->add_class("h2");
  title.set_hexpand(true);
  title.set_vexpand(true);
  title.set_valign(Gtk::Align::ALIGN_END);
  title.show();
  box.add(title);

  // This, obviously, is not a real code. It's just here as a placeholder to
  // test the layout.
  // TODO: replace with real code
  code.set_label("N-word1-word2");
  code.get_style_context()->add_class("h1");
  code.get_style_context()->add_class("code");
  code.set_hexpand(true);
  code.set_vexpand(true);
  code.set_valign(Gtk::Align::ALIGN_START);
  code.set_line_wrap(false);
  code.set_selectable(true);
  code.show();
  box.add(code);

  code.signal_button_press_event().connect(
      sigc::mem_fun(*this, &SendCodeView::on_code_button_press_event),
      /*after=*/false);
}

bool SendCodeView::on_code_button_press_event(GdkEventButton* button_event) {
  // Respond to left mouse click only.
  if (button_event->button != 1) return false;

  // Selects all the text currently in the label.
  code.select_region(/*start=*/0);

  auto clipboard = Gtk::Clipboard::get(GDK_SELECTION_CLIPBOARD);
  clipboard->set_text(code.get_text());
  return true;
}
