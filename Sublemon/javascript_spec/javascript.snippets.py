import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.js')

## ONE-LINERS ##

snippet(tabTrigger='con', description='continue', content=
'continue;'
)

snippet(tabTrigger='this', description='this.x = x', content=
'this.$1 = $1;'
)

## BLOCKS ##
