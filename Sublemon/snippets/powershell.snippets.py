from snippets_lib import *

ps = Snippets('source.powershell')

ps/'%' - ('ForEach-Object', '%{ ${0:$SELECTION} }')
ps/'?' - ('Where-Object', '?{ ${0:$SELECTION} }')

ps/blk/'begin' - 'begin'
ps/blk/'process' - 'process'
ps/blk/'end' - 'end'

ps/blk/'if' - 'if ($1)'
ps/bls/'iff' - (':one-line: if', 'if ($1)')
ps/'ife' - (':one-line: if-else', 'if ($1) { $2 } else { $0 }')

ps/blk/'ff' - ('function {}', 'function ${1:run}')

ps/'pm' - ('Parameter', '[Parameter($1)]$0')
ps/'man' - 'Mandatory'
ps/'valp' - 'ValueFromPipeline'

ps/ind/'param' - ('param', 'param (|>$0||)')
