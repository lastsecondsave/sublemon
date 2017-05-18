import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.xml",
  increase_indent_pattern = r"^.*<(?![?!])[^\/]+>\s*$",
  decrease_indent_pattern = r"^\s*<\/.*>\s*$",
  bracket_indent_next_line_pattern = r"^.*<[^>]+\s*$",
  block_comment = ['<!--', '-->']
)
