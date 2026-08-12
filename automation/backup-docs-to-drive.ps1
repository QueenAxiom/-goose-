$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Users\DELL\axiom-enterprises"
$DriveBackupRoot = "C:\Users\DELL\Google Drive Streaming\My Drive\Axiom Backups"
$DateStamp = Get-Date -Format "yyyy-MM-dd"
$DestDir = Join-Path $DriveBackupRoot $DateStamp

$Docs = @(
    "docs\content-automation-pipeline.md",
    "docs\decisions-log.md",
    "docs\daily-procedures-readiness.md",
    "automation\content-log.md",
    "automation\prospecting-log.md"
)

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

$Copied = @()
$Missing = @()

foreach ($Doc in $Docs) {
    $Src = Join-Path $RepoRoot $Doc
    if (Test-Path $Src) {
        $DestName = $Doc -replace '[\\/]', '_'
        Copy-Item -Path $Src -Destination (Join-Path $DestDir $DestName) -Force
        $Copied += $DestName
    } else {
        $Missing += $Doc
    }
}

$LogLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - copied $($Copied.Count)/$($Docs.Count) to $DestDir"
if ($Missing.Count -gt 0) {
    $LogLine += " - MISSING: $($Missing -join ', ')"
}
Add-Content -Path (Join-Path $RepoRoot "automation\backup-docs-to-drive.log") -Value $LogLine

Write-Output $LogLine

try {
    Push-Location $RepoRoot
    git add "automation\backup-docs-to-drive.log" | Out-Null
    git diff --cached --quiet --exit-code -- "automation\backup-docs-to-drive.log"
    if ($LASTEXITCODE -ne 0) {
        git commit -m "chore: update backup log $DateStamp" | Out-Null
        git push origin HEAD | Out-Null
    }
} catch {
    Write-Warning "Failed to commit/push backup log: $_"
} finally {
    Pop-Location
}
