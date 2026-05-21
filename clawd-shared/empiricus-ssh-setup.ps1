# ============================================================================
# empiricus-ssh-setup.ps1
#
# One-time setup so Aristotle (Omni-AlienWare2025) and Plato (NIETZSCHE2025)
# can SSH into Empiricus (nietzsche-i9) and run recovery commands the way
# they SSH into each other today.
#
# What it does:
#   1. Verifies OpenSSH Server is installed + running (installs if missing)
#   2. Ensures sshd is listening on :22 (restarts if not)
#   3. Enables PasswordAuthentication AND PubkeyAuthentication in sshd_config
#   4. Optionally resets the local 'aaron' password (interactive prompt)
#   5. Optionally installs one or more SSH public keys into the admin
#      authorized_keys file (interactive prompt)
#   6. Applies the restrictive ACL Windows OpenSSH requires for
#      administrators_authorized_keys (otherwise sshd silently ignores it)
#   7. Verifies firewall allows :22 inbound
#   8. Restarts sshd and confirms it's listening
#   9. Prints the SSH commands Aristotle/Plato should use
#
# Idempotent: safe to re-run. Skips work that's already done.
#
# REQUIREMENTS:
#   - Run from an ELEVATED PowerShell session (Run as Administrator)
#   - Network connectivity for `Add-WindowsCapability` if OpenSSH not installed
#
# REVERSIBILITY:
#   - The sshd_config edit is line-replace, not append. Original lines were
#     commented (default). To revert: re-comment the PasswordAuthentication
#     and PubkeyAuthentication lines this script uncomments.
#   - To revoke an installed key: open
#     C:\ProgramData\ssh\administrators_authorized_keys and delete the line.
#   - Password reset is NOT reversible without knowing the prior password.
#     Skip this section if you don't want to reset.
# ============================================================================

#requires -Version 5.1
#requires -RunAsAdministrator

$ErrorActionPreference = 'Stop'

function Write-Step($msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}

function Write-OK($msg)    { Write-Host "  [OK]   $msg" -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Info($msg)  { Write-Host "         $msg" -ForegroundColor Gray }

# ----------------------------------------------------------------------------
# STEP 1: ensure OpenSSH Server is installed
# ----------------------------------------------------------------------------
Write-Step "STEP 1: OpenSSH Server installed?"

$cap = Get-WindowsCapability -Online | Where-Object { $_.Name -like 'OpenSSH.Server*' } | Select-Object -First 1
if ($cap.State -ne 'Installed') {
    Write-Warn2 "Installing OpenSSH.Server capability (may take a minute)..."
    Add-WindowsCapability -Online -Name $cap.Name | Out-Null
    Write-OK "Installed."
} else {
    Write-OK "Already installed."
}

# ----------------------------------------------------------------------------
# STEP 2: ensure sshd service is set to automatic and running
# ----------------------------------------------------------------------------
Write-Step "STEP 2: sshd service state"

$svc = Get-Service -Name sshd
if ($svc.StartType -ne 'Automatic') {
    Set-Service -Name sshd -StartupType Automatic
    Write-OK "Set sshd to Automatic startup."
}
if ($svc.Status -ne 'Running') {
    Start-Service -Name sshd
    Write-OK "Started sshd."
} else {
    Write-OK "sshd is running."
}

# ----------------------------------------------------------------------------
# STEP 3: enable Password + Pubkey auth in sshd_config
# ----------------------------------------------------------------------------
Write-Step "STEP 3: sshd_config"

$cfg = 'C:\ProgramData\ssh\sshd_config'
if (-not (Test-Path $cfg)) { throw "sshd_config not found at $cfg" }

# Read raw, no BOM concerns since we use [IO.File]::ReadAllText / WriteAllText
$raw  = [System.IO.File]::ReadAllText($cfg)
$orig = $raw

# Backup once if no backup exists
$bk = "$cfg.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
[System.IO.File]::WriteAllText($bk, $raw)
Write-Info "Backup written: $bk"

# Uncomment / set PasswordAuthentication to yes
if ($raw -match '(?m)^\s*PasswordAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*PasswordAuthentication\s+\S+.*$', 'PasswordAuthentication yes')
} elseif ($raw -match '(?m)^\s*#\s*PasswordAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*#\s*PasswordAuthentication\s+\S+.*$', 'PasswordAuthentication yes')
} else {
    $raw += "`r`nPasswordAuthentication yes`r`n"
}

# Uncomment / set PubkeyAuthentication to yes
if ($raw -match '(?m)^\s*PubkeyAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*PubkeyAuthentication\s+\S+.*$', 'PubkeyAuthentication yes')
} elseif ($raw -match '(?m)^\s*#\s*PubkeyAuthentication\s+\S+') {
    $raw = [regex]::Replace($raw, '(?m)^\s*#\s*PubkeyAuthentication\s+\S+.*$', 'PubkeyAuthentication yes')
} else {
    $raw += "`r`nPubkeyAuthentication yes`r`n"
}

if ($raw -ne $orig) {
    [System.IO.File]::WriteAllText($cfg, $raw)
    Write-OK "Updated PasswordAuthentication=yes, PubkeyAuthentication=yes."
} else {
    Write-OK "sshd_config already has both auth modes enabled."
}

# ----------------------------------------------------------------------------
# STEP 4 (optional): reset the local 'aaron' password
# ----------------------------------------------------------------------------
Write-Step "STEP 4 (optional): reset 'aaron' local password"
Write-Info  "Skip with empty password if you only want pubkey-based auth."

$pwd = Read-Host -Prompt "New password for local 'aaron' account (or blank to skip)" -AsSecureString
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pwd))

if ([string]::IsNullOrWhiteSpace($plain)) {
    Write-Info "Password reset skipped."
} else {
    try {
        Set-LocalUser -Name 'aaron' -Password $pwd
        Write-OK "Password reset for 'aaron'."
    } catch {
        Write-Warn2 "Set-LocalUser failed: $($_.Exception.Message)"
        Write-Warn2 "If 'aaron' is a Microsoft Account on this device, change the password via Settings instead."
    }
}

# Wipe plain copy from memory ASAP
$plain = $null

# ----------------------------------------------------------------------------
# STEP 5 (optional): install SSH public keys for admin login
# ----------------------------------------------------------------------------
Write-Step "STEP 5 (optional): install authorized SSH public keys"
Write-Info  "Paste one or more SSH public keys from Aristotle and/or Plato."
Write-Info  "Format: each line should look like 'ssh-ed25519 AAAA... comment'."
Write-Info  "When finished, enter a blank line."

$keysFile = 'C:\ProgramData\ssh\administrators_authorized_keys'
$newKeys = @()
while ($true) {
    $line = Read-Host -Prompt "  paste pubkey (blank to finish)"
    if ([string]::IsNullOrWhiteSpace($line)) { break }
    if ($line -notmatch '^(ssh-(rsa|ed25519)|ecdsa-sha2-\S+)\s+\S+') {
        Write-Warn2 "  doesn't look like a valid SSH public key - skipped"
        continue
    }
    $newKeys += $line.Trim()
}

if ($newKeys.Count -gt 0) {
    # Read existing keys (if any), then write the union - no Add-Content
    # because of the fleet's documented concatenation bug
    $existing = @()
    if (Test-Path $keysFile) {
        $existing = [System.IO.File]::ReadAllLines($keysFile)
    }
    $union = ($existing + $newKeys) |
        Where-Object { $_ -and $_.Trim().Length -gt 0 } |
        Select-Object -Unique
    # Write with explicit no-BOM UTF8 encoding
    $enc = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllLines($keysFile, $union, $enc)
    Write-OK "Added $($newKeys.Count) key(s). File now has $($union.Count) key line(s)."
} else {
    Write-Info "No keys added."
}

# ----------------------------------------------------------------------------
# STEP 6: ACL on administrators_authorized_keys (Windows OpenSSH requirement)
# ----------------------------------------------------------------------------
Write-Step "STEP 6: ACL on administrators_authorized_keys"

if (Test-Path $keysFile) {
    icacls $keysFile /inheritance:r `
        /grant 'NT AUTHORITY\SYSTEM:(F)' `
        /grant 'BUILTIN\Administrators:(F)' | Out-Null
    Write-OK "ACL applied (SYSTEM + Administrators full, inheritance disabled)."
} else {
    Write-Info "administrators_authorized_keys not present; skipping ACL."
}

# ----------------------------------------------------------------------------
# STEP 7: firewall rule
# ----------------------------------------------------------------------------
Write-Step "STEP 7: firewall for :22"
$rule = Get-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
    Write-OK "Added inbound rule for TCP/22."
} else {
    if (-not $rule.Enabled) {
        Set-NetFirewallRule -DisplayName 'OpenSSH SSH Server (sshd)' -Enabled True
        Write-OK "Enabled existing rule."
    } else {
        Write-OK "Firewall rule already present and enabled."
    }
}

# ----------------------------------------------------------------------------
# STEP 8: restart sshd, verify listening
# ----------------------------------------------------------------------------
Write-Step "STEP 8: restart sshd and verify :22 listening"
Restart-Service -Name sshd -Force
Start-Sleep -Seconds 2

$listen = netstat -ano | Select-String ':22\s' | Select-String 'LISTENING'
if ($listen) {
    Write-OK "sshd is listening on :22"
    $listen | ForEach-Object { Write-Info $_.Line.Trim() }
} else {
    Write-Warn2 "sshd does NOT appear to be listening on :22 yet."
    Write-Warn2 "Check 'Get-Service sshd' and the sshd event log."
}

# ----------------------------------------------------------------------------
# STEP 9: print connection commands for Aristotle and Plato
# ----------------------------------------------------------------------------
Write-Step "STEP 9: connection commands for the peers"

# Try to find this machine's Tailscale IP
$tsIp = $null
try {
    $tsIp = (& 'C:\Program Files\Tailscale\tailscale.exe' ip -4 2>$null) | Select-Object -First 1
} catch {}
if (-not $tsIp) {
    $tsIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.InterfaceAlias -like '*Tailscale*' } |
        Select-Object -First 1 -ExpandProperty IPAddress)
}
if (-not $tsIp) { $tsIp = '<tailscale-ip-here>' }

$lanIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like '10.0.*' -or $_.IPAddress -like '192.168.*' } |
    Select-Object -First 1 -ExpandProperty IPAddress)
if (-not $lanIp) { $lanIp = '<lan-ip-here>' }

Write-Host ""
Write-Host "From Aristotle or Plato, connect via:" -ForegroundColor Green
Write-Host "  ssh aaron@$tsIp           # over Tailscale"
Write-Host "  ssh aaron@$lanIp          # over LAN"
Write-Host ""
Write-Host "If pubkey auth installed: connection should be passwordless."
Write-Host "If only password auth: it'll prompt for the password you set in Step 4."
Write-Host ""
Write-Host "Test from here locally first:" -ForegroundColor Green
Write-Host "  ssh aaron@127.0.0.1"
Write-Host "  (if this prompts for a password and accepts it, sshd is fully wired)"
Write-Host ""

Write-Host "=== DONE ===" -ForegroundColor Cyan
