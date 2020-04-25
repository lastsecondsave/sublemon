from snippets_lib import *

js = Snippets('source.js')

js/'con' - 'continue;'
js/'this' - ('this.x = x', 'this.$1 = $1;')
js/'pl' - 'console.log(${0:$SELECTION});'

js/blk/'if' - 'if ($1)'
js/blk/'else' - 'else'
js/blk/'elif' - 'else if ($1)'
js/blk/'sw' - 'switch ($1)'
js/blk/'wh' - 'while ($1)'

js/blk/'for' - ('for', 'for ($1)')
js/blk/'fore' - ('for (of)', 'for (let $1 of $2)')
js/blk/'fori' - ('for (i++)', 'for (let ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')

js/blk/'fn' - 'function ${1:run}($2)'
