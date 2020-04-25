from snippets_lib import *

regexp = Snippets('source.regexp')

regexp/'>' - ('atomic group', '(?>${0:$SELECTION})')
regexp/'=' - ('lookahead', '(?=${0:$SELECTION})')
regexp/':' - ('non-capturing group', '(?:${0:$SELECTION})')

clj = Snippets('source.clojure')

clj/'pl' - ('println', '(println $0)')
