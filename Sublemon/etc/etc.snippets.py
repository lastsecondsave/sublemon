import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.regexp')

snippet(tabTrigger='>', description='atomic group', content=
'(?>${0:$SELECTION})'
)

snippet(tabTrigger='=', description='lookahead', content=
'(?=${0:$SELECTION})'
)

snippet(tabTrigger=':', description='non-capturing group', content=
'(?:${0:$SELECTION})'
)
