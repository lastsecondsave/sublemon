from snippets_lib import *

ps = Snippets('source.powershell')

ps/blk/'if' - ('if', 'if ($1)')
ps/blk/'else' - 'else'
ps/bls/'iff' - ('if (one-line)', 'if ($1)')
ps/'ife' - ('if-else (one-line)', 'if ($1) { $2 } else { $0 }')

ps/blk/'begin' - 'begin'
ps/blk/'process' - 'process'
ps/blk/'end' - 'end'

ps/blp/'param' - 'param'

ps/blk/'fun' - 'function ${1:run}'

ps/'pm' - ('Parameter', '[Parameter($1)]')
