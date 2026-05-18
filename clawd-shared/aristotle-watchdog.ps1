# =============================================================================
# aristotle-watchdog.ps1
# Periodic health check + auto-recovery for the Aristotle Clawdbot gateway.
#
# Runs via Windows Scheduled Task "Aristotle Watchdog" every 5 minutes.
# Escalation ladder:
#   1. --check (read-only): if healthy -> done
#   2. After 2 consecutive degraded results -> --soft (restart broken pieces)
#   3. If --soft still degraded -> full recovery (kill + restart everything)
#   4. If full still failing -> emit ALERT log + Comms Hub notification
#
# Why hysteresis: transient HTTP-probe failures shouldn't trigger restarts.
# Real wedges last hours, so a 2-strike threshold catches them within ~10 min
# while filtering most flaps.
#
# Logs to: C:\tmp\clawdbot-aristotle\watchdog.log
# State:   C:\tmp\clawdbot-aristotle\watchdog-state.json
# =============================================================================

$ErrorActionPreference = 'Continue'
$PYTHON  = 'C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe'
$RECOVER = 'C:\Users\aaron\clawd-shared\aristotle_recover_v2.py'
$LOGDIR  = 'C:\tmp\clawdbot-aristotle'
$LOGFILE = Join-Path $LOGDIR 'watchdog.log'
$STATEFILE = Join-Path $LOGDIR 'watchdog-state.json'
$COMMS_HUB = 'http://127.0.0.1:3001/api/bridge/message'

if (-not (Test-Path $LOGDIR)) { New-Item -ItemType Directory -Path $LOGDIR -Force | Out-Null }

function Write-Log {
    param([string]$Level, [string]$Message)
    $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $line = "[$ts][$Level] $Message"
    Add-Content -Path $LOGFILE -Value $line -ErrorAction SilentlyContinue
}

function Get-State {
    if (Test-Path $STATEFILE) {
        try {
            return Get-Content $STATEFILE -Raw | ConvertFrom-Json
        } catch {
            Write-Log 'WARN' "state file unreadable, resetting: $_"
        }
    }
    return [PSCustomObject]@{
        consecutive_degraded = 0
        last_action_at = $null
        last_action = 'none'
        last_status = 'unknown'
        last_check_at = $null
    }
}

function Save-State {
    param($State)
    try {
        $State | ConvertTo-Json -Compress | Set-Content -Path $STATEFILE -Encoding UTF8
    } catch {
        Write-Log 'WARN' "failed to persist state: $_"
    }
}

function Invoke-Recovery {
    param([string]$Mode)  # 'check', 'soft', 'full'
    $argList = @($RECOVER)
    switch ($Mode) {
        'check' { $argList += '--check' }
        'soft'  { $argList += '--soft' }
        'full'  { }  # no flag = full hammer
    }
    $argList += '--json'

    $stdout = & $PYTHON $argList 2>$null
    if (-not $stdout) {
        Write-Log 'ERROR' "recovery script returned no output for mode=$Mode"
        return $null
    }
    try {
        return ($stdout -join "`n") | ConvertFrom-Json
    } catch {
        Write-Log 'ERROR' "could not parse JSON from ${Mode}: $_"
        Write-Log 'ERROR' ("  raw output (first 300 chars): " + (($stdout -join '|') | Out-String).Substring(0, [Math]::Min(300, ($stdout -join '|').Length)))
        return $null
    }
}

function Send-Notification {
    param([string]$Body)
    try {
        $payload = @{ to='aristotle'; from='watchdog'; body=$Body; priority='high' } | ConvertTo-Json -Compress
        Invoke-RestMethod -Uri $COMMS_HUB -Method POST -Body $payload -ContentType 'application/json' -TimeoutSec 5 | Out-Null
        Write-Log 'INFO' 'comms-hub notification sent'
    } catch {
        Write-Log 'WARN' "comms-hub notification failed (gateway may be wedged): $($_.Exception.Message)"
    }
}

# === MAIN ===
$state = Get-State
$state.last_check_at = (Get-Date).ToString('o')

# Step 1: check
$check = Invoke-Recovery -Mode 'check'
if (-not $check) {
    Write-Log 'ERROR' 'check failed to produce JSON; assuming degraded'
    $state.consecutive_degraded++
    $state.last_status = 'unknown'
    Save-State $state
    exit 1
}

$state.last_status = $check.status

# Gateway-only health: ignore ngrok.tunnel=false because NAT loopback gives
# false negatives. Real ngrok outages set ngrok.process=false, which is a
# separate, harder failure we'd still want to catch. Watchdog's job is to
# defend against the gateway-wedge cycling specifically.
$gatewayHealthy = $check.gateway.port -and $check.gateway.http
$ngrokProcessOk = $check.ngrok.process
$systemHealthy = $gatewayHealthy -and $ngrokProcessOk

if ($systemHealthy) {
    if ($state.consecutive_degraded -gt 0) {
        Write-Log 'INFO' "gateway recovered to healthy (was degraded $($state.consecutive_degraded) checks)"
        $state.consecutive_degraded = 0
    } else {
        # log a heartbeat once an hour (only when minute < 5)
        $minute = (Get-Date).Minute
        if ($minute -lt 5) {
            $tunnelNote = if ($check.ngrok.tunnel) { '' } else { ' (ngrok tunnel probe loopback-degraded, not a real outage)' }
            Write-Log 'OK' "hourly heartbeat - gateway healthy (pid=$($check.gateway.pid))$tunnelNote"
        }
    }
    Save-State $state
    exit 0
}

# Gateway or ngrok-process not healthy
$state.consecutive_degraded++
Write-Log 'WARN' "DEGRADED gw.port=$($check.gateway.port) gw.http=$($check.gateway.http) ngrok.process=$($check.ngrok.process) (strike $($state.consecutive_degraded))"

# Step 2: escalate to --soft after 2 strikes
if ($state.consecutive_degraded -lt 2) {
    Write-Log 'INFO' 'within hysteresis threshold; waiting for next check'
    Save-State $state
    exit 0
}

# F1b: Crash-loop detection guard (L45)
# Count "Starting Aristotle gateway..." in task-gateway.log over last 15 min.
# If >3, we're in a wedge loop — do NOT escalate, wait for manual intervention.
$taskGwLog = 'C:\tmp\clawdbot-aristotle\task-gateway.log'
if (Test-Path $taskGwLog) {
    $cutoff = (Get-Date).AddMinutes(-15)
    $startEntries = Get-Content $taskGwLog -Tail 100 | Where-Object {
        $_ -match '^\[(.+?)\] Starting Aristotle gateway' -and
        [DateTime]::TryParse($Matches[1], [ref]$null) -and
        [DateTime]::Parse($Matches[1]) -gt $cutoff
    }
    if ($startEntries -and $startEntries.Count -gt 3) {
        Write-Log 'ERROR' "WEDGE_LOOP_DETECTED: $($startEntries.Count) gateway starts in last 15 min. NOT escalating. Manual intervention required."
        # Emit Ledger event
        try {
            $body = @{ event_type='status_update'; event_subtype='crash_loop_detected'; agent='aristotle'; decision_rationale="L45: $($startEntries.Count) gateway restarts in 15 min, watchdog refusing to escalate" } | ConvertTo-Json -Compress
            Invoke-RestMethod -Uri 'http://127.0.0.1:3003/events' -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
        } catch {}
        Save-State $state
        exit 0
    }
}

Write-Log 'WARN' 'escalating to --soft recovery'
$soft = Invoke-Recovery -Mode 'soft'
$state.last_action_at = (Get-Date).ToString('o')
$state.last_action = 'soft'
if ($soft -and $soft.status -eq 'healthy') {
    Write-Log 'INFO' "soft recovery succeeded: action=$($soft.action_taken)"
    Send-Notification "Aristotle watchdog: gateway auto-recovered via --soft (was $($check.status))"
    $state.consecutive_degraded = 0
    $state.last_status = 'healthy'
    Save-State $state
    exit 0
}

# Step 3: full hammer
Write-Log 'ERROR' "soft recovery failed (status=$($soft.status)); escalating to full"
$full = Invoke-Recovery -Mode 'full'
$state.last_action_at = (Get-Date).ToString('o')
$state.last_action = 'full'
if ($full -and $full.status -eq 'healthy') {
    Write-Log 'INFO' 'full recovery succeeded'
    Send-Notification "Aristotle watchdog: gateway auto-recovered via FULL hammer (soft did not work)"
    $state.consecutive_degraded = 0
    $state.last_status = 'healthy'
    Save-State $state
    exit 0
}

# Step 4: give up; alert
Write-Log 'ALERT' "FULL RECOVERY FAILED status=$($full.status); manual intervention required"
Send-Notification "Aristotle watchdog: ALERT - automatic recovery FAILED. Aristotle is down."
Save-State $state
exit 2
