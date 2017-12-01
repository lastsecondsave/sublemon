#!/usr/bin/env zsh

set -e

case $(uname -s) in
  'Darwin') INSTALL_PATH='/Applications/Sublime Text.app/Contents/MacOS';;
  'Linux')  INSTALL_PATH='/opt/sublime_text_3';;
esac

if [[ ! -d $INSTALL_PATH ]]; then
  INSTALL_PATH="$(dirname $0)/../../../.."
fi

PACKAGES_DIRECTORY="$INSTALL_PATH/Packages"
TEMP_DIRECTORY='/tmp/sublemon'

pushd "$(dirname $0)/.."
SUBLEMON_DIRECTORY=$PWD
popd

echo "Packages directory: $(tput setaf 2)$PACKAGES_DIRECTORY$(tput sgr0)"

rm -rf $TEMP_DIRECTORY
mkdir $TEMP_DIRECTORY

cp $PACKAGES_DIRECTORY/*.sublime-package $TEMP_DIRECTORY

pushd $TEMP_DIRECTORY

for package in *.sublime-package; do
  dir="${package%%.sublime-package}"

  if [[ $(unzip -l $package | grep '__patched__') ]]; then
    echo "Skipping $(tput setaf 1)$dir$(tput sgr0).sublime-package"
    continue
  fi

  echo "Processing $(tput setaf 3)$dir$(tput sgr0).sublime-package"

  unzip -q "$package" -d "$dir"
  rm "$package"

  pushd "$dir"

  rm -rf 'Snippets'
  find . -name '*.sublime-snippet' -exec rm -f {} +
  find . -name '*.sublime-completions' -exec rm -f {} +

  if [[ $dir == 'Python' ]]; then
    rm -f 'Python.sublime-build'
    patch -b 'Python.sublime-syntax' \
        "$SUBLEMON_DIRECTORY/python_spec/Python.sublime-syntax.patch"

  elif [[ $dir == 'Java' ]]; then
    rm -f 'JavaC.sublime-build' \
          'Ant.sublime-build'

  elif [[ $dir == 'Default' ]]; then
    # patch -b 'Default (Windows).sublime-keymap' \
    #     "$SUBLEMON_DIRECTORY/etc/Default (Windows).sublime-keymap.patch"

    cp 'Default (OSX).sublime-keymap' 'Default (OSX).sublime-keymap.orig'
    cp 'Default (Linux).sublime-keymap' 'Default (Linux).sublime-keymap.orig'

    cp 'Default (Windows).sublime-keymap' 'Default (OSX).sublime-keymap'
    cp 'Default (Windows).sublime-keymap' 'Default (Linux).sublime-keymap'
  fi

  touch '__patched__'

  zip -rq "../$package" *

  popd
done

popd

cp $TEMP_DIRECTORY/*.sublime-package $PACKAGES_DIRECTORY
rm -rf $TEMP_DIRECTORY
