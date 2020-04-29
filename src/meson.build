src_includes = include_directories('.')

views = library(
    'views',
    ['views.cc', 'views.hh'],
    include_directories: [src_includes],
    dependencies: [gtkmm, granite],
)

views_dep = declare_dependency(
    link_with: [views],
    include_directories: [src_includes],
)

tree_navigation = library(
    'tree_navigation',
    ['tree_navigation.cc', 'tree_navigation.hh'],
    include_directories: [src_includes],
    dependencies: [gtkmm],
)

tree_navigation_dep = declare_dependency(
    link_with: [tree_navigation],
    include_directories: [src_includes],
)

executable(
    meson.project_name(),
    ['main.cc', bifrost_resources],
    dependencies: [views_dep, tree_navigation_dep, gtkmm, granite],
    install: true
)
