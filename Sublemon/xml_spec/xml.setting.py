import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("source.xml",
  increase_indent_pattern = r"^.*<(?![?!])[^\/]+>\s*$",
  decrease_indent_pattern = r"^\s*<\/.*>\s*$",
  bracket_indent_next_line_pattern = r"^.*<[^>]+\s*$",
  block_comment = ['<!--', '-->']
)
