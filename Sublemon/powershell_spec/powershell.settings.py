import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.powershell",
    increase_indent_pattern = [
    ],
    decrease_indent_pattern = [
    ],
    line_comment = '#',
    block_comment = ['<#', '#>']
)
