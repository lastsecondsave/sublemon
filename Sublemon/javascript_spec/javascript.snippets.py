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

snippet(tabTrigger='td', description='TODO', content=
'// TODO: '
)

snippet(tabTrigger='log', description='console.log', content=
'console.log(${0:$SELECTION});'
)

## BLOCKS ##

snippet(tabTrigger='fore', description='for each', content=
"""
for (let $1 of $2) {
    $0
}
""")

snippet(tabTrigger='fori', description='for i', content=
"""
for (let ${1:i} = 0; $1 < ${2:imax}; ${3:$1++}) {
    $0
}
""")

snippet(tabTrigger='ff', description='function', content=
"""
function ${1:run}($2) {
    $0
}
""")

snippet(tabTrigger='fa', description='anonymous function', content=
"""
function($1) {
    $0
}
""")

snippet(tabTrigger='fo', description='function (json)', content=
"""
${1:run}: function($2) {
    $0
}
""")
