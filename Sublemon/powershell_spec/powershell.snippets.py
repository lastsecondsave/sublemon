import sys
sys.path.append('../lib')
from snippets import Snippets

ps = Snippets('source.powershell')
bl = ps.with_suffix(' {\n\t$0\n}')

ps['%'] = ('ForEach-Object', '%{ ${0:$SELECTION} }')
ps['?'] = ('Where-Object', '?{ ${0:$SELECTION} }')

bl.begin = 'begin'
bl.process = 'process'
bl.end = 'end'

bl['if'] = ('if', 'if ($1)')
ps['iff'] = ('if (one-line)', 'if ($1) { $0 }')

bl.ff = ('function', 'function ${1:run}')

ps.pm = ('Parameter', '[Parameter($1)]$0')
ps.man = 'Mandatory'
ps.valp = 'ValueFromPipeline'

ps.param = ('param',
"""
param (
    $0
)
""")
