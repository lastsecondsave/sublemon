Add-Type -Assembly System.IO.Compression.FileSystem

Push-Location
Set-Location '..\..\..\..\Packages'

gci '*.sublime-package' | %{
    $packageZip = $_.FullName
    $package =  Join-Path $(pwd) $_.BaseName

    [System.IO.Compression.ZipFile]::ExtractToDirectory($packageZip, $package)
    del $packageZip
    del $package\*.sublime-snippet
    [System.IO.Compression.ZipFile]::CreateFromDirectory($package, $packageZip)
    del -r $package

    "$packageZip processed"
}

Pop-Location
