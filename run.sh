#!/bin/sh

readonly _GRESOURCE='data/com.github.jmc-88.bifrost.gresource'

env _DEBUG_RESOURCE_PATH="$(realpath "${_GRESOURCE}")" \
  python3 -m src.bifrost
