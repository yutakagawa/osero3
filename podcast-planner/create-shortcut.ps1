# Podcast Planner - create shortcuts (Desktop + Start menu) with the microphone icon
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $dir 'start-podcast-planner.bat'
$icon = Join-Path $dir 'icon.ico'
$ws = New-Object -ComObject WScript.Shell
$folders = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))
foreach ($folder in $folders) {
  $lnk = $ws.CreateShortcut((Join-Path $folder 'Podcast企画ボード.lnk'))
  $lnk.TargetPath = $target
  $lnk.WorkingDirectory = $dir
  $lnk.IconLocation = $icon
  $lnk.WindowStyle = 7
  $lnk.Description = 'Podcast企画ボード'
  $lnk.Save()
}
Write-Host ''
Write-Host 'ショートカットを作成しました(デスクトップとスタートメニュー)。'
Write-Host 'スタートメニューを開き「Podcast企画ボード」を右クリックして「スタートにピン留めする」を選んでください。'
Write-Host ''
