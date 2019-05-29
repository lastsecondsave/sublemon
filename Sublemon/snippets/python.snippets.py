from snippets_lib import *

def blk(s): return s + ':\n\t$0'

py = Snippets('source.python')

py/spc/'im' - 'import'
py/spc/'fim' - 'from $1 import'
py/spc/'ret' - 'return'
py/spc/'yi' - 'yield'

py/'stm' - '@staticmethod'

py/'pl' - 'print(${0:$SELECTION})'

py/'ss' - ('self.x = x', 'self.$1 = $1')
py/'doc' - ('docstring', '"""\n\t$0\n"""')
py/'isi' - ('isinstance()', 'isinstance(${1:$SELECTION}, ${2:str})')

py/blk/'def' - ('function()', 'def ${1:run}($2)')
py/spc/'lam' - ('lambda', 'lambda ${1:x}:')

py/blk/'class' - 'class $1'
py/blk/'init' - ('__init__()', 'def __init__(self$1)')

py/blk/'if' - 'if $1'
py/'ife' - 'if $1 else $0'
py/blk/'else' - 'else'
py/blk/'elif' - 'elif $1'
py/blk/'while' - 'while $1'

py/blk/'for' - ('for', 'for $1 in $2')
py/blk/'fori' - (':range: for', 'for ${1:i} in range(${2:0}, ${3:imax})')

py/'lc' - (':list: comprehension', '[$1 for $2 in $3]')
py/'tc' - (':tuple: comprehension', '($1 for $2 in $3)')
py/'dc' - (':dict: comprehension', '{$1: $2 for $3 in $4}')
