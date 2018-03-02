import sys
sys.path.append('../lib')
from snippets import Snippets

py = Snippets('source.python')
kw = py.with_suffix(' ')
bl = py.with_suffix(':\n\t$0\n')

kw.ret = 'return'

py.pl = ('print', 'print(${0:$SELECTION})')
py['self'] = 'self.'

py.ss = ('self.x = x', 'self.$1 = $1')
py.doc = ('docstring', '"""\n\t$0\n"""')

bl['def'] = ('function', 'def ${1:run}($2)')

bl['if'] = ('if', 'if $1')
bl['else'] = 'else'
bl['elif'] = ('elif', 'elif $1')
bl['while'] = ('while', 'while $1')
bl['for'] = ('for', 'for $1 in $2')
