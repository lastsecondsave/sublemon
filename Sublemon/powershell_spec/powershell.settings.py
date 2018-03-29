import sys
sys.path.append("../lib")
from settings import settings

settings("source.powershell",
    line_comment = '#',
    block_comment = ['<#', '#>']
)
