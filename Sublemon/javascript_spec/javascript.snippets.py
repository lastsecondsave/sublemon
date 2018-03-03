import sys
sys.path.append('../lib')
from snippets import Snippets

js = Snippets('source.js')
bl = js.with_suffix(' {\n\t$0\n}')

js.con = ('continue', 'continue;')
js.this = ('this.x = x', 'this.$1 = $1;')
js.log = ('console.log', 'console.log(${0:$SELECTION});')

bl.fore = ('for each', 'for (let $1 of $2)')
bl.fori = ('for i', 'for (let ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')

bl.ff = ('function', 'function ${1:run}($2)')
bl.fa = ('anonymous function', 'function($1)')
bl.fp = ('function (json)', '${1:run}: function($2)')
