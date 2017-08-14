import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("source.powershell",
    increase_indent_pattern = [
    ],
    decrease_indent_pattern = [
    ],
    line_comment = '#',
    block_comment = ['<#', '#>']
)
