Push-Location -Path '..'

gci -r '*.settings.py' | %{
    Push-Location -Path $_.DirectoryName
    Write-Output "`nRunning $($_.Name) in $(pwd)`n"
    python $_.Name
    Pop-Location
}

Set-Location "disco"
Write-Output "`nRunning disco.py in $(pwd)`n"
python disco.py

Pop-Location
