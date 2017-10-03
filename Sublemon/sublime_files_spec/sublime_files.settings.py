import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("meta.context.sublime-syntax entity.name.key",
    show_in_symbol_list=1,
    show_in_indexed_symbol_list=1
)
