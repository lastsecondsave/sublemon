import sys
sys.path.append('../lib')
from snippets import Snippets


py = Snippets('source.python')
py_sp = py.with_space()
py_bl = py.with_suffix(':\n\t$0\n')

py_sp.im = 'import'
py_sp.fim = 'from $1 import'
py_sp.ret = 'return'

py.stm = '@staticmethod'

py.pl = 'print(${0:$SELECTION})'

py.ss = ('self.x = x', 'self.$1 = $1')
py.doc = ('docstring', '"""\n\t$0\n"""')

py_bl['def'] = ('function()', 'def ${1:run}($2)')

py_bl['class'] = 'class $1'
py_bl.init = ('__init__()', 'def __init__(self$1)')

py_bl['if'] = 'if $1'
py['ife'] = 'if $1 else $0'
py_bl['else'] = 'else'
py_bl['elif'] = 'elif $1'
py_bl['while'] = 'while $1'

py_bl['for'] = ('for', 'for $1 in $2')
py_bl.fori = (':range: for', 'for ${1:i} in range(${2:0}, ${3:imax})')

py.lc = (':list: comprehension', '[$1 for $2 in $3]')
py.tc = (':tuple: comprehension', '($1 for $2 in $3)')
py.dc = (':dict: comprehension', '{$1: $2 for $3 in $4}')
