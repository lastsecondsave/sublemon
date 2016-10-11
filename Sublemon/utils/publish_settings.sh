#!/bin/zsh

set -e

publish() {
  pushd $(dirname $1)
  echo "Running $(tput setaf 3)$(basename $1)$(tput sgr0) in $(tput setaf 2)$PWD$(tput sgr0)\n"
  python $(basename $1)
  echo
  popd
}

pushd "$(dirname $0)/.."

for spy in $(find . -name '*.settings.py'); do
  publish $spy
done;

publish "disco/disco.py"

popd
