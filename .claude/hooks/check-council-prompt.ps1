$StateFile = ".claude/state/last-council-prompt-date.txt"
$StateDir = Split-Path -Parent $StateFile

if (-not (Test-Path $StateDir)) {
  New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
}

$Hour = (Get-Date).Hour
$Today = (Get-Date).ToString('yyyy-MM-dd')
$Last = ""

if (Test-Path $StateFile) {
  $Last = (Get-Content $StateFile -Raw).Trim()
}

if ($Hour -ge 6 -and $Last -ne $Today) {
  $Today | Set-Content -Path $StateFile -NoNewline

  $output = @{
    hookSpecificOutput = @{
      hookEventName = "UserPromptSubmit"
      additionalContext = "This is the first user message received after 6am local time today. Before or alongside addressing the user's actual message, ask: Do you or Axiom have any questions for the council?"
    }
  }

  $output | ConvertTo-Json -Compress
}
