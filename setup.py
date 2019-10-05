#!/usr/bin/python3

import glob
import os
import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py


class CustomBuildPyCommand(build_py):
    """Compiles GTK resources on top of the stock build command."""

    def run(self):
        source = os.path.join("data", "com.github.jmc-88.bifrost.gresource.xml")
        self.execute(
            subprocess.call,
            args=(["glib-compile-resources", source, "--sourcedir=data"],),
            msg="running glib-compile-resources",
        )

        return super().run()


setup(
    name="bifrost",
    version="0.1",
    author="Daniele Cocca",
    description="Send your files to another computer over the Internet",
    url="https://github.com/jmc-88/bifrost",
    license="BSD 3-Clause Clear License",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"gui_scripts": ["com.github.jmc-88.bifrost = bifrost.bifrost:main"]},
    cmdclass={"build_py": CustomBuildPyCommand},
    data_files=[
        ("share/applications", ["data/com.github.jmc-88.bifrost.desktop"]),
        ("share/metainfo", ["data/com.github.jmc-88.bifrost.appdata.xml"]),
        ("share/icons/hicolor/scalable/apps", ["data/com.github.jmc-88.bifrost.svg"]),
        (
            "share/com.github.jmc-88.bifrost",
            ["data/com.github.jmc-88.bifrost.gresource"],
        ),
    ],
)
