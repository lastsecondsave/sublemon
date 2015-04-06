filter MavenFilter() {
    if ($_ -match '\[ERROR\] Failed to execute goal.*') { $skip = $true}
    if ($skip -or $_ -match '\[INFO\] -+') { return }
    $_
}
