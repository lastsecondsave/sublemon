import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.powershell",
    increaseIndentPatterns = [
    ],
    decreaseIndentPatterns = [
    ],
    line_comment = '# ',
    block_comment = ['<#', '#>']
)
