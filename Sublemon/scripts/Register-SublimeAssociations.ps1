$RootKey = 'hkcu:'

$SublimeExe = '"' + $env:USERPROFILE + '\Software\sublime-text\sublime_text.exe"'
$SublimeNode = "$RootKey\Software\SublimeText"

$Default = '(Default)'

function New-RootItem($Path) {
    if (Test-Path $Path) { Remove-Item -Recurse $Path }
    New-Item $Path
}

function New-ClassDefinition($Name, $Icon) {
    New-RootItem "$RootKey\Software\Classes\$Name"

    New-Item "$RootKey\Software\Classes\$Name\DefaultIcon"
    Set-ItemProperty "$RootKey\Software\Classes\$Name\DefaultIcon" -Name $Default -Value $Icon

    New-Item "$RootKey\Software\Classes\$Name\shell"
    Set-ItemProperty "$RootKey\Software\Classes\$Name\shell" -Name $Default -Value 'open'

    New-Item "$RootKey\Software\Classes\$Name\shell\open"
    New-Item "$RootKey\Software\Classes\$Name\shell\open\command"

    Set-ItemProperty "$RootKey\Software\Classes\$Name\shell\open\command" -Name $Default -Value "$SublimeExe `"%1`""
}

function Set-Association($Extension, $Class) {
    Set-ItemProperty "$SublimeNode\Capabilities\FileAssociations" -Name ".$Extension" -Value $Class; "Registered $Extension"
}

$(
    New-ClassDefinition 'SublimeTextFile' '%SystemRoot%\SysWow64\imageres.dll,-102'
    New-ClassDefinition 'SublimeTextItem' "$SublimeExe,0"

    New-RootItem $SublimeNode

    New-Item "$SublimeNode\Capabilities"
    Set-ItemProperty "$SublimeNode\Capabilities" -Name ApplicationName -Value 'Sublime Text'
    Set-ItemProperty "$SublimeNode\Capabilities" -Name ApplicationDescription -Value 'A sophisticated text editor for code, markup and prose'

    New-Item "$SublimeNode\Capabilities\FileAssociations"
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
    'go',
    'py',
    'ps1', 'psm1',
    'sh', 'zsh',
    'sql',
    'css',
    'gitignore', 'gitattributes'
)

$TextFiles    | ForEach-Object { Set-Association $_ 'SublimeTextFile' }
$SublimeFiles | ForEach-Object { Set-Association "sublime-$_" 'SublimeTextFile' }
$SublimeItems | ForEach-Object { Set-Association "sublime-$_" 'SublimeTextItem' }

Set-ItemProperty "$RootKey\Software\RegisteredApplications" -Name 'Sublime Text' -Value 'Software\SublimeText\Capabilities'
