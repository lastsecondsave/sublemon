param(
  [Parameter(Mandatory=$False,Position=0)]$Command
)

$host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(2048, 512)

$script = '.\powershell_exec.ps1'
if (-not (Test-Path $script)) { iex $Command; return }

& $script $Command
