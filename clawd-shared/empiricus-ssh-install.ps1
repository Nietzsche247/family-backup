# ============================================================================
# empiricus-ssh-install.ps1
#
# Non-interactive variant of empiricus-ssh-setup.ps1 with both peer pubkeys
# pre-baked. Single run, no prompts. Must be run elevated.
#
# What it does:
#   1. Verify sshd installed + running
#   2. Uncomment PubkeyAuthentication in sshd_config (leave PasswordAuth off)
#   3. Write Aristotle's + Plato's pubkeys to administrators_authorized_keys
#   4. Apply restrictive ACL the Windows OpenSSH admin path requires
#   5. Restart sshd
#   6. Verify :22 listening
#   7. Print test commands for Aristotle/Plato
# ============================================================================

#requires -Version 5.1
#requires -RunAsAdministrator

$ErrorActionPreference = 'Stop'

function W-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function W-OK($m)   { Write-Host "  [OK]   $m" -ForegroundColor Green }
function W-Warn($m) { Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function W-Info($m) { Write-Host "         $m" -ForegroundColor Gray }

# Peer pubkeys to install (from Aaron's collection on Aristotle + Plato)
$peerKeys = @(
    'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOBO4ljyTaDbDcKHOKYYF6RcEH1kI3JRDw29T3uAM46F aristotle->empiricus',
    'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ7RawQ/Es1+Ld5YRoiSO5VIDGR3T66/nLq2lkT98Ut5 plato->empiricus'
)

# ---------- STEP 1: sshd service ----------
W-Step 'STEP 1: sshd service state'
$svc = Get-Service -Name sshd -ErrorAction SilentlyContinue
if (-not $svc) { throw 'sshd service not installed' }
if ($svc.StartType -ne 'Automatic') {
    Set-Service -Name sshd -StartupType Automatic
    W-OK 'Set sshd to Automatic startup'
}
if ($svc.Status -ne 'Running') {
    Start-Service -Name sshd
    W-OK 'Started sshd'
} else {
    W-OK 'sshd already running'
}

# ---------- STEP 2: sshd_config — uncomment PubkeyAuthentication ----------
W-Step 'STEP 2: sshd_config — enable PubkeyAuthentication'
$cfg = 'C:\ProgramData\ssh\sshd_config'
$raw = [System.IO.File]::ReadAllText($cfg)
$orig = $raw

# Backup once
$bk = "$cfg.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
[System.IO.File]::WriteAllText($bk, $raw)
W-Info "Backup: $bk"

if ($raw -match '(?m)^\s*PubkeyAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*PubkeyAuthentication\s+\S+.*$', 'PubkeyAuthentication yes')
    W-OK 'PubkeyAuthentication line normalized to "yes"'
} elseif ($raw -match '(?m)^\s*#\s*PubkeyAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*#\s*PubkeyAuthentication\s+\S+.*$', 'PubkeyAuthentication yes')
    W-OK 'Uncommented PubkeyAuthentication and set to "yes"'
} else {
    $raw += "`r`nPubkeyAuthentication yes`r`n"
    W-OK 'Appended PubkeyAuthentication yes (none found)'
}

if ($raw -ne $orig) {
    # no-BOM UTF-8
    $enc = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($cfg, $raw, $enc)
    W-OK 'sshd_config saved (no BOM)'
} else {
    W-Info 'sshd_config unchanged'
}

# ---------- STEP 3: write authorized_keys ----------
W-Step 'STEP 3: administrators_authorized_keys'
$adminKeys = 'C:\ProgramData\ssh\administrators_authorized_keys'

# Read existing real key lines (skip comments + blanks)
$existing = @()
if (Test-Path $adminKeys) {
    $existing = [System.IO.File]::ReadAllLines($adminKeys) |
        Where-Object { $_ -and $_.Trim() -and ($_.Trim() -notmatch '^#') }
    W-Info "Existing non-comment lines: $($existing.Count)"
}

# Union — Select-Object -Unique preserves first occurrence, comparing whole line
$union = ($existing + $peerKeys) | Where-Object { $_ } | Select-Object -Unique

$enc = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($adminKeys, $union, $enc)
W-OK "Wrote $($union.Count) key line(s) to $adminKeys (no BOM)"

# Verify each line is on its own row (defensive against historic Add-Content concat bug)
$check = [System.IO.File]::ReadAllLines($adminKeys) | Where-Object { $_ -and $_.Trim() }
$multiKeyLines = $check | Where-Object { ($_ -split '\s+ssh-(rsa|ed25519|ecdsa-)').Count -gt 2 }
if ($multiKeyLines) {
    W-Warn 'Detected multiple ssh keys on a single line — FIX MANUALLY'
} else {
    W-OK 'Verified each key is on its own line'
}

# ---------- STEP 4: ACL ----------
W-Step 'STEP 4: restrictive ACL on administrators_authorized_keys'
$icaclsOut = icacls $adminKeys /inheritance:r `
    /grant 'NT AUTHORITY\SYSTEM:(F)' `
    /grant 'BUILTIN\Administrators:(F)' 2>&1
W-OK "ACL applied"
W-Info ($icaclsOut -join ' ')

# ---------- STEP 5: firewall ----------
W-Step 'STEP 5: firewall :22'
$rule = Get-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
    W-OK 'Added inbound rule for TCP/22'
} elseif (-not $rule.Enabled) {
    Set-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' -Enabled True
    W-OK 'Enabled existing rule'
} else {
    W-OK 'Firewall rule present + enabled'
}

# ---------- STEP 6: restart sshd ----------
W-Step 'STEP 6: restart sshd'
Restart-Service -Name sshd -Force
Start-Sleep -Seconds 2
$svc = Get-Service sshd
W-OK "sshd status after restart: $($svc.Status)"

# ---------- STEP 7: verify :22 listening ----------
W-Step 'STEP 7: verify :22 listening'
$listen = netstat -ano | Select-String ':22\s' | Select-String 'LISTENING'
if ($listen) {
    W-OK 'sshd is listening on :22'
    $listen | ForEach-Object { W-Info $_.Line.Trim() }
} else {
    W-Warn 'No :22 listener visible in netstat (try again in 5s or check Get-NetTCPConnection -LocalPort 22)'
}

# ---------- STEP 8: print test commands ----------
W-Step 'STEP 8: test commands for the peers'

$tsIp = $null
try { $tsIp = (& 'C:\Program Files\Tailscale\tailscale.exe' ip -4 2>$null) | Select-Object -First 1 } catch {}
if (-not $tsIp) {
    $tsIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.InterfaceAlias -like '*Tailscale*' } |
        Select-Object -First 1 -ExpandProperty IPAddress)
}
if (-not $tsIp) { $tsIp = '<tailscale-ip>' }

Write-Host ""
Write-Host "From Aristotle, test with:" -ForegroundColor Green
Write-Host "  ssh -i C:\Users\aaron\.ssh\<aristotle-private-key> aaron@$tsIp `"hostname`""
Write-Host ""
Write-Host "From Plato, test with:" -ForegroundColor Green
Write-Host "  ssh -i C:\Users\Aaron\.ssh\<plato-private-key> aaron@$tsIp `"hostname`""
Write-Host ""
Write-Host "Expected response: Nietzsche-i9"
Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Cyan
