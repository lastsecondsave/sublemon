from snippets_lib import *

sh = Snippets('source.shell')

sh/'awk' - "awk '{$0}'"

sh/ind/'case' - 'case $1 in>=>$0==>esac'
sh/ind/'if' - 'if [[ $1 ]]; then>=>$0==>fi'
