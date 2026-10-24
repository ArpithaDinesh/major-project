$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "MindSync.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = """C:\Users\user\Desktop\Major project\run-mindsync.vbs"""
$Shortcut.WorkingDirectory = "C:\Users\user\Desktop\Major project"
$Shortcut.Description = "Launch MindSync AI Personal Knowledge Vault"
$Shortcut.Save()
Write-Output "Successfully created MindSync desktop shortcut at $ShortcutPath"
