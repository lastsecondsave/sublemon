import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.yaml",
  increase_indent_pattern = [
    r"^.*:\s*[>|]?\s*$",
    r"^\s*-\s+.*$",
  ],
  decrease_indent_pattern = r"^\s*-\s+.*$",
  line_comment = '#'
)
