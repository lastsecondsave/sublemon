import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.python')

## KEYWORDS ##

## ONE-LINERS ##

snippet(tabTrigger='pl', description='print', content=
'print(${0:$SELECTION})'
)

snippet(tabTrigger='self', description='self.x = x', content=
'self.$1 = $1'
)

## BLOCKS ##

snippet(tabTrigger='def', description='function', content=
"""
def ${1:run}($2):
    $0
""")

snippet(tabTrigger='doc', description='docstring', content=
'''
"""
$0
"""
''')

snippet(tabTrigger='if', description='if', content=
"""
if $1:
    $0
""")

snippet(tabTrigger='else', description='else', content=
"""
else:
    $0
""")

snippet(tabTrigger='elif', description='elif', content=
"""
elif $1:
    $0
""")

snippet(tabTrigger='while', description='while', content=
"""
while $1:
    $0
""")

snippet(tabTrigger='for', description='for', content=
"""
for $1 in $2:
    $0
""")
