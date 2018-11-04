import sys
sys.path.append('../lib')
from snippets import Snippets


js = Snippets('source.js')
js_bl = js.with_braces()
js_bls = js.with_same_line_braces()

js.con = 'continue;'
js.tt = ('this.x = x', 'this.$1 = $1;')
js.log = 'console.log(${0:$SELECTION});'

js_bl['if'] = 'if ($1)'
js_bl['else'] = 'else'
js_bl['elif'] = 'else if ($1)'
js_bl['switch'] = 'switch ($1)'
js_bl['while'] = 'while ($1)'

js_bl['for'] = ('for () {}', 'for ($1)')
js_bl.fore = (':each: for () {}', 'for (let $1 of $2)')
js_bl.fori = (':i: for () {}', 'for (let ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')

js_bl.ff = ('function () {}', 'function ${1:run}($2)')
js_bl.ffa = (':anon: function () {}', 'function($1)')
js_bls.fla = (':oneline: :anon: function () {}', 'function($1)')
js_bl.ffj = (':json: function () {}', '${1:run}: function($2)')
