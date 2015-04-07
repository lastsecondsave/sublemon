param(
  [Parameter(Mandatory=$False)]$Command,
  [Parameter(Mandatory=$False)]$Context
)

$host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(2048, 512)

if ($Context -and (Test-Path $Context)) { . $Context }

$script = '.\powershell_exec.ps1'
if (Test-Path $script) { & $script $Command; return }

iex $Command
