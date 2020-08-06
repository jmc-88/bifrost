#!/bin/sh
set -eu

readonly _GRESOURCE='data/com.github.jmc-88.bifrost.gresource'

python3 setup.py build || exit 1

env _DEBUG_RESOURCE_PATH="$(realpath "${_GRESOURCE}")" \
  python3 -m src.bifrost || exit 1
