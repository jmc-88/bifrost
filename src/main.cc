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

#include <granite.h>
#include <gtkmm.h>

#include "views.hh"

static const char kApplicationId[] = "com.github.jmc-88.bifrost";

// Opens $XDG_DOWNLOAD_DIR with the default file manager.
static void ShowDownloads() {
  auto downloads_dir =
      Glib::get_user_special_dir(GUserDirectory::G_USER_DIRECTORY_DOWNLOAD);
  if (downloads_dir.empty()) {
    g_error("Couldn't find a value for $XDG_DOWNLOAD_DIR");
    return;
  }

  if (!Gio::AppInfo::launch_default_for_uri("file://" + downloads_dir)) {
    g_error("Couldn't open \"%s\"", downloads_dir.c_str());
    return;
  }
}

class BifrostWindow : public Gtk::ApplicationWindow {
 public:
  BifrostWindow() {
    auto action_group = Gio::SimpleActionGroup::create();
    action_group->add_action("close", [this] { close(); });
    insert_action_group("bifrost", action_group);

    set_title("Bifrost");
    set_default_size(400, 400);
    set_deletable(true);
    set_resizable(false);
    get_style_context()->add_class("rainbow");
    get_style_context()->add_class("rounded");

    headerbar.set_title(get_title());
    headerbar.set_show_close_button(true);
    headerbar.get_style_context()->add_class(GTK_STYLE_CLASS_FLAT);
    headerbar.pack_start(back_button);
    headerbar.pack_end(spinner);
    headerbar.show();
    set_titlebar(headerbar);

    back_button.set_label("Back");
    back_button.get_style_context()->add_class(GRANITE_STYLE_CLASS_BACK_BUTTON);
    back_button.signal_clicked().connect([] { g_warning("**TODO**\n"); });

    spinner.start();

    // TODO: welcome_view.signal_send_selected.connect(...);
    // TODO: welcome_view.signal_receive_selected.connect(...);
    welcome_view.signal_downloads_selected.connect(
        sigc::ptr_fun(ShowDownloads));
    welcome_view.show();
    add(welcome_view);
  }

 private:
  Gtk::Button back_button = Gtk::Button("Back");
  Gtk::Spinner spinner;
  Gtk::HeaderBar headerbar;
  WelcomeView welcome_view;
};

int main(int argc, char* argv[]) {
  auto app = Gtk::Application::create(argc, argv, kApplicationId);
  app->set_accel_for_action("bifrost.close", "<Primary>q");

  auto css_provider = Gtk::CssProvider::create();
  css_provider->signal_parsing_error().connect(
      [](const Glib::RefPtr<const Gtk::CssSection>& section,
         const Glib::Error& error) {
        g_error("CSS loading error in %s, from [%d:%d] to [%d:%d]: %s",
                section->get_file()->get_uri().c_str(),
                section->get_start_line(), section->get_start_position(),
                section->get_end_line(), section->get_end_position(),
                error.what().c_str());
      });
  css_provider->load_from_resource(
      "/com/github/jmc-88/bifrost/application.css");

  Gtk::StyleContext::add_provider_for_screen(
      Gdk::Screen::get_default(), css_provider,
      GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);

  BifrostWindow main_window;
  main_window.show();
  return app->run(main_window);
}