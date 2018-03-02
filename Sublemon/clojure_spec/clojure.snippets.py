import sys
sys.path.append('../lib')
from snippets import Snippets

clj = Snippets('source.clojure')

clj.pl = ('println', '(println $0)')

