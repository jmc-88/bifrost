#!/bin/sh
#
# Simple Git pre-commit hook to check the formatting of C/C++ sources.
# Optionally allows for auto-formatting of sources.
#
# Accepts the following 'git config' options:
#
#   hooks.clangformat.check-only - boolean, indicates wheter the hook should
#       just check the validity of source code formatting, or otherwise to
#       automatically and silently fix it instead.
#       It's best to leave this set to 'true' and integrate clang-format with
#       the text editor, as allowing it to automatically reformat file contents
#       can have it undo format-only changes in the tree and can lead to empty
#       commits...
#       Defaults to 'true'.
#
#   hooks.clangformat.binary - path, executable name or path to clang-format.
#       Defaults to 'clang-format'.
#
#   hooks.clangformat.style - string, code style as accepted by clang-format's
#       '-style' command line flag. It is only applied if the configuration
#       file given by hooks.clangformat.config doesn't exist.
#       Defaults to 'Google'.
#
#   hooks.clangformat.config - string, path to the .clang-format configuration file
#       to use. Has precedence over hooks.clangformat.style.
#       Defaults to '${GIT_PROJECT_ROOT}/.clang-format'.


CLANGFORMAT_CMDLINE=''  # filled in by main()

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  readonly GIT_TARGET_REVISION='HEAD'
else
  # Initial commit: diff against an empty tree object
  readonly GIT_TARGET_REVISION='4b825dc642cb6eb9a060e54bf8d69288fbee4904'
fi


tmpfile() {
  # https://unix.stackexchange.com/a/181996
  # POSIX sh doesn't include mktemp(1), but it does include m4,
  # which exposes mkstemp(3)... wat.
  echo 'mkstemp(template)' |
    m4 -D template="${TMPDIR:-/tmp}/clang_format_hook.XXXXXX"
}

clang_format_apply() {
  CLANGFORMAT_FILENAME="${1?}"

  # https://github.com/koalaman/shellcheck/wiki/SC2089
  set -- ${CLANGFORMAT_CMDLINE} -i "${CLANGFORMAT_FILENAME}"
  "${@}"
}

clang_format_diff() {
  CLANGFORMAT_FILENAME="${1?}"
  CLANGFORMAT_TMPFILE="$(tmpfile)"

  # https://github.com/koalaman/shellcheck/wiki/SC2089
  set -- ${CLANGFORMAT_CMDLINE} "${CLANGFORMAT_FILENAME}"
  "${@}" > "${CLANGFORMAT_TMPFILE}"

  git diff --no-index --exit-code "${CLANGFORMAT_FILENAME}" "${CLANGFORMAT_TMPFILE}"
  CLANGFORMAT_EXIT_CODE=${?}

  rm -f "${CLANGFORMAT_TMPFILE}"
  return ${CLANGFORMAT_EXIT_CODE}
}

git_config_option() {
  OPTION_TYPE="${1?}"
  if expr "${OPTION_TYPE}" : '^--' >/dev/null; then
    shift
  else
    OPTION_TYPE=""
  fi

  OPTION_NAME="${1?}"
  OPTION_DEFAULT_VALUE="${2?}"

  # https://github.com/koalaman/shellcheck/wiki/SC2089
  set -- git config --get ${OPTION_TYPE} "${OPTION_NAME}"
  OPTION_VALUE="$("${@}")"

  [ -n "${OPTION_VALUE}" ] && echo "${OPTION_VALUE}" || echo "${OPTION_DEFAULT_VALUE}"
}

git_modified_sources() {
  for filename in $(git diff-index --cached --name-only "${GIT_TARGET_REVISION}"); do
    if expr "${filename}" : '^.\+\.\(c\|cc\|cpp\|C\|h\|hh\|hpp\|H\)$' >/dev/null; then
      echo "${filename}"
    fi
  done
}

has_executable() {
  EXECUTABLE_NAME="${1?}"

  command -v "${EXECUTABLE_NAME}" >/dev/null
}

main() {
  readonly GIT_PROJECT_ROOT="$(git rev-parse --show-toplevel)"
  readonly CLANGFORMAT_CHECK_ONLY="$(git_config_option --bool 'hooks.clangformat.check-only' true)"
  readonly CLANGFORMAT_BINARY="$(git_config_option --path 'hooks.clangformat.binary' 'clang-format')"
  readonly CLANGFORMAT_STYLE="$(git_config_option 'hooks.clangformat.style' 'Google')"
  readonly CLANGFORMAT_CONFIG="$(git_config_option 'hooks.clangformat.config' "${GIT_PROJECT_ROOT}/.clang-format")"

  if ! has_executable "${CLANGFORMAT_BINARY}"; then
    echo 1>&2 " :: Cannot find \"${CLANGFORMAT_BINARY}\"."
    exit 1
  fi

  CLANGFORMAT_CMDLINE="${CLANGFORMAT_BINARY}"
  if [ -f "${CLANGFORMAT_CONFIG}" ]; then
    CLANGFORMAT_CMDLINE="${CLANGFORMAT_CMDLINE} -style=file -assume-filename='${CLANGFORMAT_CONFIG}' -fallback-style=none"
  else
    CLANGFORMAT_CMDLINE="${CLANGFORMAT_CMDLINE} -style='${CLANGFORMAT_STYLE}'"
  fi

  CLANGFORMAT_FAIL=false
  if ${CLANGFORMAT_CHECK_ONLY}; then
    for filename in $(git_modified_sources); do
      if ! clang_format_diff "${filename}"; then
        CLANGFORMAT_FAIL=true
      fi
    done
  else
    for filename in $(git_modified_sources); do
      if clang_format_apply "${filename}" && git add "${filename}"; then
        echo " :: Reformatted \"${filename}\"."
      else
        CLANGFORMAT_FAIL=true
      fi
    done
  fi

  if ${CLANGFORMAT_FAIL}; then
    echo 1>&2
    echo 1>&2 " :: clang-format pre-commit hook failed."
    exit 1
  fi
}

main "${@}"
