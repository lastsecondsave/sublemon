filter MavenFilter() {
    if ($_ -match '\[INFO\] -+') { return }
    if ($_ -match '\[ERROR\] Failed to execute goal.*') { $skip = $true}
    if ($skip -and $_ -match '\[[EIW]\w+\].*') { return }
    $_
}
