from snippets_lib import *

sh = Snippets('source.shell')

sh/'#!' - '#!/usr/bin/env bash'
sh/'awk' - "awk '{$0}'"

sh/ind/'case' - 'case $1 in>=>$0==>esac'
sh/ind/'if' - 'if [[ $1 ]]; then>=>$0==>fi'
sh/ind/'while' - 'while $1; do>=>$0==>done'
