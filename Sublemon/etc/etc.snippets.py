import sys
sys.path.append('../lib')
from snippets import Snippets

regexp = Snippets('source.regexp')

regexp['>'] = ('atomic group', '(?>${0:$SELECTION})')
regexp['='] = ('lookahead', '(?=${0:$SELECTION})')
regexp[':'] = ('non-capturing group', '(?:${0:$SELECTION})')
