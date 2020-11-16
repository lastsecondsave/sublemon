from snippets_lib import *

def blk(s): return s + ':\n\t$0'

py = Snippets('source.python')

py/'pl' - 'print(${0:$SELECTION})'

py/'self' - ('self.x = x', 'self.$1 = $1')

py/blk/'def' - 'def ${1:run}($2)'
py/blk/'init' - ('__init__', 'def __init__(self$1)')
py/blk/'inm' - ('if __name__ == "__main__"', 'if __name__ == "__main__"')

py/'pld' - '# pylint: disable='
