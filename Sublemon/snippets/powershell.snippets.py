from snippets_lib import *

ps = Snippets('source.powershell')

ps/'%' - '%{ ${0:$SELECTION} }'
ps/'?' - '?{ ${0:$SELECTION} }'

ps/blk/'if' - 'if ($1)'
ps/bls/'iff' - (':one-line: if', 'if ($1)')
ps/'ife' - (':one-line: if-else', 'if ($1) { $2 } else { $0 }')

ps/blk/'else' - 'else'

ps/blk/'begin' - 'begin'
ps/blk/'process' - 'process'
ps/blk/'end' - 'end'

ps/blk/'fun' - ('function {}', 'function ${1:run}')

ps/'pm' - ('Parameter', '[Parameter($1)]')

ps/ind/'param' - ('param', 'param (>=>$0==>)')

ps/spc/'cd' - 'Set-Location'
ps/spc/'cp' - 'Copy-Item'
ps/spc/'echo' - 'Write-Output'
ps/spc/'fl' - 'Format-List'
ps/spc/'ft' - 'Format-Table'
ps/spc/'gc' - 'Get-Content'
ps/spc/'gci' - 'Get-ChildItem'
ps/spc/'ls' - 'Get-ChildItem'
ps/spc/'mv' - 'Move-Item'
ps/spc/'ni' - 'New-Item'
ps/spc/'popd' - 'Pop-Location'
ps/spc/'pushd' - 'Push-Location'
ps/spc/'pwd' - 'Get-Location'
ps/spc/'rm' - 'Remove-Item'
ps/spc/'sls' - 'Select-String'
ps/spc/'tee' - 'Tee-Object'
