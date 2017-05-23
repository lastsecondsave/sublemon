#!/usr/bin/env zsh

set -e

case $(uname -s) in
  'Darwin') INSTALL_PATH='/Applications/Sublime Text.app/Contents/MacOS';;
  'Linux')  INSTALL_PATH='/opt/sublime_text_3';;
esac

if [[ ! -d $INSTALL_PATH ]]; then
  INSTALL_PATH="$(dirname $0)/../../../.."
fi

echo "Packages directory: $(tput setaf 2)$INSTALL_PATH/Packages$(tput sgr0)"

pushd -q "$INSTALL_PATH/Packages"

mkdir bac

for package in *.sublime-package; do
  dir="${package%%.sublime-package}"
  echo "Cleaning $(tput setaf 3)$dir$(tput sgr0).sublime-package"

  unzip -q "$package" -d "$dir"
  mv "$package" bac

  pushd "$dir"

  rm -rf 'Snippets'
  for snippet in $(find . -name '*.sublime-snippet'); do
    rm $snippet
  done

  if [[ $dir == 'Python' ]]; then
    rm -f 'Python.sublime-build'
  fi

  zip -rq "../$package" *

  popd
  rm -rf "$dir"
done

rm -rf bac

popd -q
