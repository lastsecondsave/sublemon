Push-Location

Set-Location "..\.."
gci -r '*.settings.py' | %{
    cd $_.DirectoryName
    Write-Output "`nRunning $($_.Name) in $(pwd)`n"
    python $_.Name
}

Pop-Location
Push-Location

Set-Location "..\..\Disco\build"
Write-Output "`nRunning disco.py in $(pwd)`n"
python disco.py

Pop-Location
