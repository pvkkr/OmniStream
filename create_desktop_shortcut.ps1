$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ShortcutPath = Join-Path $DesktopPath "OmniStream - Video Downloader & VLC.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

$AppDir = $PSScriptRoot
if (-not $AppDir) { $AppDir = (Get-Location).Path }
$TargetBat = Join-Path $AppDir "run.bat"

$Shortcut.TargetPath = $TargetBat
$Shortcut.WorkingDirectory = $AppDir
$Shortcut.Description = "OmniStream - Video Downloader & VLC Player"

# Use VLC icon if available
$VlcPath = "C:\Program Files\VideoLAN\VLC\vlc.exe"
if (Test-Path $VlcPath) {
    $Shortcut.IconLocation = "$VlcPath, 0"
}

$Shortcut.Save()
Write-Host "Desktop shortcut created successfully at: $ShortcutPath"
