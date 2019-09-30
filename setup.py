#!/usr/bin/python3

import glob
import os
from distutils.core import setup

setup(
    name="Bifrost",
    version="0.1",
    author="Daniele Cocca",
    description="Send your files to another computer over the Internet",
    url="https://github.com/jmc-88/bifrost",
    license="BSD 3-Clause Clear License",
    scripts=["com.github.jmc-88.bifrost"],
    packages=["bifrost"],
    data_files=[
        ("share/applications", ["data/com.github.jmc-88.bifrost.desktop"]),
        ("share/metainfo", ["data/com.github.jmc-88.bifrost.appdata.xml"]),
        ("share/icons/hicolor/128x128/apps", ["data/com.github.jmc-88.bifrost.svg"]),
        ("bin/bifrost", ["src/bifrost/main.py"]),
        ("bin/bifrost", ["src/bifrost/__init__.py"]),
    ],
)
