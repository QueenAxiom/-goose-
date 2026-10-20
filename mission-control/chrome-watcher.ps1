# Keeps the Mission Control helper running while Chrome is open, and restarts it when its code changes.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 8765
$sourceGlobs = "*.py", "*.html", "*.js", "*.css", "*.json"

function Get-NewestSourceTime {
    (Get-ChildItem -Path (Join-Path $here "*") -File -Include $sourceGlobs -ErrorAction SilentlyContinue |
        Measure-Object -Property LastWriteTime -Maximum).Maximum
}

while ($true) {
    if (Get-Process chrome -ErrorAction SilentlyContinue) {
        $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($listener) {
            $proc = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
            if ($proc -and (Get-NewestSourceTime) -gt $proc.StartTime) {
                Stop-Process -Id $proc.Id -Force
                Start-Sleep -Seconds 2
                $listener = $null
            }
        }
        if (-not $listener) {
            $py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
            if (-not $py) { $py = (Get-Command python.exe).Source }
            Start-Process -FilePath $py -ArgumentList "control.py" -WorkingDirectory $here -WindowStyle Hidden
            Start-Sleep -Seconds 20
        }
    }
    Start-Sleep -Seconds 5
}
