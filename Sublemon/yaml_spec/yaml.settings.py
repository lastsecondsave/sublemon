import sys
sys.path.append("../lib")
from settings import settings

settings("source.yaml",
    increase_indent_pattern = [
        r"^.*:\s*[>|]?\s*$",
        r"^\s*-\s+.*$",
    ],
    decrease_indent_pattern = r"^\s*-\s+.*$",
    line_comment = '#'
)
