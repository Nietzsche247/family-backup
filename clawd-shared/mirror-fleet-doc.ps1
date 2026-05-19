#requires -Version 5.1
<#
.SYNOPSIS
  Mirror NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md from nietzsche-i9 (Empiricus)
  to Aristotle and Plato's clawd-shared folders.

.DESCRIPTION
  Run from elevated PowerShell on nietzsche-i9. Will scp the local fleet doc
  to both peer machines over Tailscale, then verify via SHA-256.

  Auth: tries existing id_ed25519 key first. If that key isn't authorized on the
  peer, OpenSSH falls back to password — you'll be prompted in this window.

  Host-key acceptance: uses `-o StrictHostKeyChecking=accept-new` so first-time
  fingerprint for Aristotle is auto-saved (Plato is already in known_hosts).

  Idempotent: safe to re-run. Verification re-hashes after every push.
#>

$ErrorActionPreference = 'Stop'

# ---------- config ----------
$SrcFile = 'C:\Users\aaron\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md'

$Targets = @(
  @{
    Name     = 'Aristotle (Omni-AlienWare2025)'
    User     = 'aaron'
    Ip       = '100.108.47.36'
    DestWin  = 'C:\Users\aaron\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md'
    DestScp  = '/C:/Users/aaron/clawd-shared/NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md'
  },
  @{
    Name     = 'Plato (NIETZSCHE2025)'
    User     = 'Aaron'   # capital A on Plato
    Ip       = '100.73.106.82'
    DestWin  = 'C:\Users\Aaron\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md'
    DestScp  = '/C:/Users/Aaron/clawd-shared/NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md'
  }
)

# ---------- preflight ----------
Write-Host '=== NorthStar fleet doc mirror ===' -ForegroundColor Cyan
Write-Host ''

if (-not (Test-Path $SrcFile)) {
  Write-Host "FATAL: source file not found: $SrcFile" -ForegroundColor Red
  exit 1
}

$srcInfo  = Get-Item $SrcFile
$srcHash  = (Get-FileHash $SrcFile -Algorithm SHA256).Hash
$srcLines = (Get-Content $SrcFile).Count
Write-Host "Source:  $SrcFile" -ForegroundColor Gray
Write-Host "  size:  $($srcInfo.Length) bytes"
Write-Host "  lines: $srcLines"
Write-Host "  sha256: $srcHash"
Write-Host ''

$scp = (Get-Command scp.exe -ErrorAction SilentlyContinue).Source
$ssh = (Get-Command ssh.exe -ErrorAction SilentlyContinue).Source
if (-not $scp -or -not $ssh) {
  Write-Host 'FATAL: scp.exe / ssh.exe not on PATH. Install OpenSSH client: ' -ForegroundColor Red
  Write-Host '  Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0'
  exit 1
}
Write-Host "scp: $scp"
Write-Host "ssh: $ssh"
Write-Host ''

# ---------- push + verify ----------
$results = @()

foreach ($t in $Targets) {
  Write-Host "----- $($t.Name) [$($t.Ip)] -----" -ForegroundColor Yellow

  $scpDest = "$($t.User)@$($t.Ip):$($t.DestScp)"
  $sshTarget = "$($t.User)@$($t.Ip)"

  # Push
  Write-Host "scp -> $scpDest"
  & $scp -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $SrcFile $scpDest
  $scpExit = $LASTEXITCODE
  if ($scpExit -ne 0) {
    Write-Host "  SCP FAILED (exit $scpExit). Skipping verify for this host." -ForegroundColor Red
    $results += [pscustomobject]@{ Host = $t.Name; Pushed = $false; HashMatch = $null; RemoteHash = $null }
    Write-Host ''
    continue
  }
  Write-Host '  scp ok' -ForegroundColor Green

  # Verify via remote sha256 (PowerShell over SSH)
  $remoteCmd = "powershell -NoProfile -Command `"(Get-FileHash '$($t.DestWin)' -Algorithm SHA256).Hash`""
  Write-Host 'verifying remote sha256...'
  $remoteHash = (& $ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $sshTarget $remoteCmd 2>&1 | Select-Object -Last 1).Trim()

  $match = ($remoteHash -eq $srcHash)
  if ($match) {
    Write-Host "  remote sha256: $remoteHash  MATCH" -ForegroundColor Green
  } else {
    Write-Host "  remote sha256: $remoteHash" -ForegroundColor Red
    Write-Host "  local  sha256: $srcHash"
    Write-Host '  MISMATCH' -ForegroundColor Red
  }

  $results += [pscustomobject]@{ Host = $t.Name; Pushed = $true; HashMatch = $match; RemoteHash = $remoteHash }
  Write-Host ''
}

# ---------- summary ----------
Write-Host '=== SUMMARY ===' -ForegroundColor Cyan
$results | Format-Table -AutoSize

$allOk = ($results.Count -eq $Targets.Count) -and ($results | Where-Object { -not $_.HashMatch }).Count -eq 0
if ($allOk) {
  Write-Host 'All mirrors verified. Done.' -ForegroundColor Green
  exit 0
} else {
  Write-Host 'One or more hosts failed. See output above.' -ForegroundColor Red
  exit 2
}
