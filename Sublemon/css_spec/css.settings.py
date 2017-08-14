import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("source.css",
  block_comment = ['/*', '*/']
)

settings("source.css meta.rule.selector.css",
  show_in_symbol_list = 1,
  symbol_transformation = [
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g"
  ]
)

settings("source.css meta.at-rule.body.css meta.rule.selector.css",
  show_in_symbol_list = 1,
  symbol_transformation = [
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g",
    r"s/^/    /g"
  ]
)
