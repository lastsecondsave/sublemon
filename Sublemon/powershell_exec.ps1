param($Command, $Context)

$host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(2048, 512)
$script = '.\powershell_exec.ps1'

if ($Context -and (Test-Path $Context)) { . $Context }

if (Test-Path $script) {
    & $script $Command
} else {
    Invoke-Expression $Command
}
