#ifndef BIFROST_SRC_TREE_NAVIGATION_HH
#define BIFROST_SRC_TREE_NAVIGATION_HH

#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <cassert>
#include <unordered_map>
#include <utility>

class TreeNavigation : public Gtk::Stack {
 public:
  using RootWidget = std::nullptr_t;

  template <typename T>
  using ChildWidget = T;

  template <typename T>
  static ChildWidget<T> ChildOf(T&& widget) {
    return std::forward<T>(widget);
  }

  void add(Gtk::Widget& widget, RootWidget /*has_no_parent*/);
  void add(Gtk::Widget& widget, ChildWidget<Gtk::Widget&> parent);
  bool back();
  void set_visible_child(Gtk::Widget& widget);

  using event_signal_t = sigc::signal<void>;
  event_signal_t signal_enter_root_widget;
  event_signal_t signal_leave_root_widget;

 private:
  Gtk::Widget* root_widget = nullptr;
  std::unordered_map<Gtk::Widget*, Gtk::Widget*> widget_to_parent;

  bool set_root_widget(Gtk::Widget& widget);
};

#endif  //  BIFROST_SRC_TREE_NAVIGATION_HH
