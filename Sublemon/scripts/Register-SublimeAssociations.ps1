$SublimeExe = "${env:ProgramFiles}\Sublime Text\sublime_text.exe"
$SublimeNode = "HKCU:\Software\SublimeText"

function New-RootItem($Path) {
    if (Test-Path $Path) { Remove-Item -Recurse $Path }
    New-Item $Path
}

function New-ClassDefinition($Name, $Icon) {
    $Class = "HKCU:\Software\Classes\$Name"
    $Default = '(Default)'

    New-RootItem $Class

    New-Item "$Class\DefaultIcon"
    Set-ItemProperty "$Class\DefaultIcon" -Name $Default -Value $Icon

    New-Item "$Class\shell"
    Set-ItemProperty "$Class\shell" -Name $Default -Value 'open'

    New-Item "$Class\shell\open", "$Class\shell\open\command"
    Set-ItemProperty "$Class\shell\open\command" -Name $Default -Value "`"$SublimeExe`" `"%1`""
}

function Set-Association($Extension, $Class) {
    Set-ItemProperty "$SublimeNode\Capabilities\FileAssociations" -Name ".$Extension" -Value $Class
    Write-Output "Registered .$Extension"
}

$(
    New-ClassDefinition 'SublimeTextFile' '%SystemRoot%\SysWow64\imageres.dll,-102'
    New-ClassDefinition 'SublimeTextItem' "$SublimeExe,1"

    New-RootItem $SublimeNode

    New-Item "$SublimeNode\Capabilities"
    Set-ItemProperty "$SublimeNode\Capabilities" -Name 'ApplicationName' -Value 'Sublime Text'
    Set-ItemProperty "$SublimeNode\Capabilities" -Name 'ApplicationDescription' -Value 'A sophisticated text editor for code, markup and prose'

    New-Item "$SublimeNode\Capabilities\FileAssociations"

    Set-ItemProperty "HKCU:\Software\RegisteredApplications" -Name 'Sublime Text' -Value 'Software\SublimeText\Capabilities'
) | Out-Null

$SublimeItems = 'project', 'workspace'

$SublimeFiles = @(
    'settings', 'keymap', 'mousemap',
    'menu', 'commands',
    'theme', 'color-scheme',
    'syntax', 'completions', 'snippet', 'build'
)

$TextFiles = @(
    'txt', 'log', 'conf', 'csv',
    'md', 'markdown',
    'ini', 'toml',
    'xml', 'xsd',
    'yaml', 'yml',
    'java', 'properties', 'groovy', 'clj', 'gradle', 'kt',
    'js', 'json',
    'c', 'cpp', 'cu', 'h', 'hpp',
    'rs',
    'go', 'mod',
    'py',
    'ps1', 'psm1',
    'sh', 'zsh',
    'sql',
    'css',
    'gitignore', 'gitattributes', 'gitmodules'
)

$TextFiles    | ForEach-Object { Set-Association $_ 'SublimeTextFile' }
$SublimeFiles | ForEach-Object { Set-Association "sublime-$_" 'SublimeTextFile' }
$SublimeItems | ForEach-Object { Set-Association "sublime-$_" 'SublimeTextItem' }
