import sys
sys.path.append("../lib")
from settings import settings

settings("source.ini",
    line_comment = [';', '#']
)

settings("source.ini entity.name.section",
    show_in_symbol_list = 1
)

settings("source.unix",
    line_comment = '#'
)

settings("text.rfc entity.name.title",
    show_in_symbol_list = 1
)
