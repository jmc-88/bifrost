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

executable(
    meson.project_name(),
    ['main.cc', bifrost_resources],
    dependencies: [views_dep, gtkmm, granite],
    install: true
)
