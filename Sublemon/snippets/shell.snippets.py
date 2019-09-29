from snippets_lib import *

sh = Snippets('source.shell')

sh/'awk' - ('awk', "awk '{$0}'")

sh/ind/'case' - ('case', 'case $1 in>=>$0==>esac')

sh/ind/'if' - ('if', 'if [[ $1 ]]; then>=>$0==>fi')

sh/blk/'ff' - ('function', '$1()')
