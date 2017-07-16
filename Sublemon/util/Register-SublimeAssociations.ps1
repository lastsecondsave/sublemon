$RootKey = 'hkcu:'
# $Workaround = $True

$SublimeExe = '"c:\Software\Sublime Text 3\sublime_text.exe"'
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

    $Exe = if ($Workaround) { 'notepad.exe' } else { $SublimeExe }
    Set-ItemProperty "$RootKey\Software\Classes\$Name\shell\open\command" -Name $Default -Value "$Exe `"%1`""
}

function Set-Association($Extension, $Class) {
    Set-ItemProperty "$SublimeNode\Capabilities\FileAssociations" -Name ".$Extension" -Value $Class; "Registered $Extension"
}

%{
    New-ClassDefinition 'SublimeTextFile' '%SystemRoot%\SysWow64\imageres.dll,-102'
    New-ClassDefinition 'SublimeTextItem' "$SublimeExe,0"

    New-RootItem $SublimeNode

    New-Item "$SublimeNode\Capabilities"
    Set-ItemProperty "$SublimeNode\Capabilities" -Name ApplicationName -Value 'Sublime Text'
    Set-ItemProperty "$SublimeNode\Capabilities" -Name ApplicationDescription -Value 'The thing that makes your life better'

    New-Item "$SublimeNode\Capabilities\FileAssociations"
} | Out-Null

$SublimeItems = 'project', 'workspace'
$SublimeFiles = 'syntax', 'settings', 'snippet', 'build', 'theme', 'keymap', 'mousemap', 'completions', 'menu', 'commands'
$TextFiles = @(
    'txt', 'log', 'conf', 'csv',
    'md', 'markdown',
    'ini',
    'xml', 'xsd',
    'yaml', 'yml',
    'java', 'properties', 'groovy', 'clj', 'gradle',
    'js', 'json',
    'c', 'cpp', 'cu', 'h', 'hpp',
    'go',
    'py',
    'ps1', 'psm1',
    'sh',
    'sql',
    'css',
    'gitignore', 'gitattributes'
)

$TextFiles    | %{ Set-Association $_ 'SublimeTextFile' }
$SublimeFiles | %{ Set-Association "sublime-$_" 'SublimeTextFile' }
$SublimeItems | %{ Set-Association "sublime-$_" 'SublimeTextItem' }

Set-ItemProperty "$RootKey\Software\RegisteredApplications" -Name 'Sublime Text' -Value 'Software\SublimeText\Capabilities'
