#!/bin/zsh

set -e

pushd '/opt/sublime_text_3/Packages'

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

popd
