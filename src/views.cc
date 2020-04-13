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

#include "views.hh"

WelcomeView::WelcomeView() {
  welcome = granite_widgets_welcome_new("Welcome to Bifrost",
                                        "What would you like to do?");
  granite_widgets_welcome_append(welcome, "document-export", "Send Files",
                                 "Upload data to another computer");
  granite_widgets_welcome_append(welcome, "document-import", "Receive Files",
                                 "Download data from another computer");
  granite_widgets_welcome_append(welcome, "folder", "Show Downloads",
                                 "Open your Downloads folder");

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
