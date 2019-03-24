from snippets import *

js = Snippets('source.js')

js/'con' - 'continue;'
js/'tt' - ('this.x = x', 'this.$1 = $1;')
js/'log' - 'console.log(${0:$SELECTION});'

js/blk/'if' - 'if ($1)'
js/blk/'else' - 'else'
js/blk/'elif' - 'else if ($1)'
js/blk/'switch' - 'switch ($1)'
js/blk/'while' - 'while ($1)'

js/blk/'for' - ('for () {}', 'for ($1)')
js/blk/'fore' - (':each: for () {}', 'for (let $1 of $2)')
js/blk/'fori' - (':i: for () {}', 'for (let ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')

js/blk/'ff' - ('function () {}', 'function ${1:run}($2)')
js/blk/'ffa' - (':anon: function () {}', 'function($1)')
js/bls/'fla' - (':oneline: :anon: function () {}', 'function($1)')
js/blk/'ffj' - (':json: function () {}', '${1:run}: function($2)')
