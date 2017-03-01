#!/usr/bin/env zsh

set -e

case $(uname -s) in
  'Darwin') INSTALL_PATH='/Applications/Sublime Text.app/Contents/MacOS';;
  'Linux')  INSTALL_PATH='/opt/sublime_text_3';;

  *) echo 'Unknown OS'; exit 1;;
esac

pushd -q "$INSTALL_PATH/Packages"

for package in *.sublime-package; do
  echo "Cleaning $package"
  dir="${package%%.sublime-package}"

  unzip -q "$package" -d "$dir"
  rm "$package"

  pushd "$dir"

  rm -rf 'Snippets'
  for snippet in $(find . -name '*.sublime-snippet'); do
    rm $snippet
  done

  zip -rq "$package" *
  mv "$package" ..

  popd

  rm -rf "$dir"
done

popd -q
