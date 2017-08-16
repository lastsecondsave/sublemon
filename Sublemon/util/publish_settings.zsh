#!/usr/bin/env zsh

set -e

publish() {
  pushd "$(dirname $1)"
  echo "Running $(tput setaf 3)$(basename $1)$(tput sgr0) in $(tput setaf 2)$PWD$(tput sgr0)\n"
  python "$(basename $1)"
  echo
  popd
}

pushd "$(dirname $0)/.."

for settings in $(find . -name '*.settings.py'); do
  publish $settings
done;

for snippets in $(find . -name '*.snippets.py'); do
  publish $snippets
done;

publish "disco/disco.py"
publish "disco/icons.py"

popd
