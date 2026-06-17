$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcut = Join-Path $desktop 'AR Dashboard.lnk'
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($shortcut)
$sc.TargetPath = Join-Path $here 'AR_Dashboard.bat'
$sc.WorkingDirectory = $here
$sc.IconLocation = (Join-Path $here 'euro.ico') + ',0'
$sc.Description = 'AR Collection Dashboard - double click to launch'
$sc.WindowStyle = 1
$sc.Save()
Write-Output ("Created: " + $shortcut)
