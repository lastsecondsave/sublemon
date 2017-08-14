import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("source.shell",
    increase_indent_pattern = [
        r".*\{\s*$",
        r"\s*(if\s.+;\s*)?then\s*$",
        r"\s*case\s.*\sin\s*$"
    ],
    decrease_indent_pattern = [
        r"\s*\}.*$",r"\s*(fi|esac)\s*.*$"
    ],
    line_comment = '#'
)
