#include "tree_navigation.hh"

void TreeNavigation::add(Gtk::Widget& widget,
                         TreeNavigation::RootWidget /*has_no_parent*/) {
  assert(root_widget == nullptr);
  Gtk::Stack::add(widget);
  set_root_widget(widget);
}

void TreeNavigation::add(Gtk::Widget& widget,
                         TreeNavigation::ChildWidget<Gtk::Widget&> parent) {
  Gtk::Stack::add(widget);
  widget_to_parent.emplace(&widget, &parent);
}

bool TreeNavigation::back() {
  auto it = widget_to_parent.find(get_visible_child());
  if (it == widget_to_parent.end()) return false;
  set_visible_child(*it->second);
  return true;
}

void TreeNavigation::set_visible_child(Gtk::Widget& widget) {
  Gtk::Stack::set_visible_child(widget);

  auto it = widget_to_parent.find(get_visible_child());
  if (it == widget_to_parent.end())
    signal_enter_root_widget.emit();
  else
    signal_leave_root_widget.emit();
}

bool TreeNavigation::set_root_widget(Gtk::Widget& widget) {
  auto children = get_children();
  if (std::find(children.begin(), children.end(), &widget) == children.end())
    return false;

  root_widget = &widget;
  return true;
}
