from snippets_lib import *

ps = Snippets('source.powershell')

ps/'pl' - 'Write-Output $0'

ps/blk/'if' - 'if ($1)'
ps/blk/'else' - 'else'

ps/blk/'bg' - 'begin'
ps/blk/'pr' - 'process'
ps/blk/'en' - 'end'
ps/blk/'fn' - 'function ${1:run}'

ps/blp/'pm' - 'param'

with ps.completions() as cmp:
    cmp.group(["function", "", "Cmdlet"],
              "Copy-Item",
              "ForEach-Object",
              "Format-List",
              "Format-Table",
              "Get-ChildItem",
              "Get-Content",
              "Get-Location",
              "Join-Path",
              "Move-Item",
              "New-Item",
              "Pop-Location",
              "Push-Location",
              "Remove-Item",
              "Resolve-Path",
              "Select-Object",
              "Select-String",
              "Set-Location",
              "Sort-Object",
              "Tee-Object",
              "Test-Path",
              "Write-Error",
              "Write-Host",
              "Write-Output")
