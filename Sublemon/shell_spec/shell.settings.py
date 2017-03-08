import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.shell",
    increaseIndentPatterns = [
        r".*\{\s*$",
        r"\s*(if\s.+;\s*)?then\s*$",
        r"\s*case\s.*\sin\s*$"
    ],
    decreaseIndentPatterns = [
        r"\s*\}.*$",r"\s*(fi|esac)\s*.*$"
    ],
    line_comment = '# '
)
