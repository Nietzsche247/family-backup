# ledger-audit.ps1 — NorthStar Ledger Audit
# Compares registered resources against what is actually installed/running.
# Run weekly or on-demand to maintain write-through discipline.
#
# Usage:
#   .\ledger-audit.ps1
#   .\ledger-audit.ps1 -LedgerUrl "http://127.0.0.1:3003"
#   .\ledger-audit.ps1 -OutputFile "C:\Users\aaron\clawd-shared\audit-report.md"

param(
    [string]$LedgerUrl  = "http://127.0.0.1:3003",
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Continue"
$lines = [System.Collections.Generic.List[string]]::new()

function Log {
    param([string]$msg)
    Write-Host $msg
    $lines.Add($msg)
}

function Sep {
    param([string]$title)
    Log ""
    Log "## $title"
    Log ("---" * 20)
}

# Header
Log "# NorthStar Ledger Audit"
Log ("**Run:** " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Log ("**Host:** " + $env:COMPUTERNAME)

# STEP 1: Pull ledger registrations
Sep "Ledger Registrations"

$ledgerResources = @()
$ledgerReachable = $false
$ledgerNames = @{}

try {
    $resp = Invoke-RestMethod -Uri "$LedgerUrl/query" -Method GET -TimeoutSec 5 -ErrorAction Stop
    $ledgerReachable = $true
    if ($resp -is [array]) {
        $ledgerResources = $resp
    } elseif ($resp.results) {
        $ledgerResources = $resp.results
    } elseif ($resp.data) {
        $ledgerResources = $resp.data
    } else {
        $ledgerResources = @($resp)
    }
    Log ("Ledger reachable. Resources registered: " + $ledgerResources.Count)
    foreach ($r in $ledgerResources) {
        $rname = if ($r.name)  { $r.name  } else { $r.id }
        $rtype = if ($r.type)  { $r.type  } else { "unknown" }
        $rpath = if ($r.path)  { $r.path  } elseif ($r.url) { $r.url } else { "(no path)" }
        Log ("  [$rtype] $rname -- $rpath")
        if ($rname) { $ledgerNames[$rname.ToLower()] = $r }
    }
} catch {
    Log ("WARNING: Ledger unreachable at $LedgerUrl -- " + $_.Exception.Message)
}

# STEP 2: Scan machine for known tools/services
Sep "Machine Scan"

$found = [System.Collections.Generic.List[hashtable]]::new()

# PM2 processes
Log "### PM2 Services"
try {
    $pm2Raw = & pm2 jlist 2>$null
    if ($pm2Raw) {
        $pm2List = $pm2Raw | ConvertFrom-Json -ErrorAction Stop
        foreach ($proc in $pm2List) {
            $ePath = if ($proc.pm2_env.pm_exec_path) { $proc.pm2_env.pm_exec_path } else { "(pm2)" }
            $entry = @{ name = $proc.name; type = "service"; path = $ePath; status = $proc.pm2_env.status; source = "pm2" }
            $found.Add($entry)
            Log ("  [pm2] " + $proc.name + " -- " + $proc.pm2_env.status + " -- " + $ePath)
        }
    } else {
        Log "  (no pm2 processes or pm2 not available)"
    }
} catch {
    Log ("  WARNING: pm2 scan failed: " + $_.Exception.Message)
}

# MemPalace
Log ""
Log "### MemPalace"
$mpPath = "C:\Users\aaron\mempalace-venv\Scripts\mempalace.exe"
if (Test-Path $mpPath) {
    $found.Add(@{ name = "mempalace"; type = "tool"; path = $mpPath; source = "filesystem" })
    Log ("  FOUND: " + $mpPath)
} else {
    Log "  NOT FOUND at expected path"
}

# Graphify
Log ""
Log "### Graphify"
$gpDirs = Get-ChildItem "C:\Users\aaron\clawd-shared\graphify-out*" -Directory -ErrorAction SilentlyContinue
if ($gpDirs) {
    foreach ($d in $gpDirs) {
        $found.Add(@{ name = ("graphify-" + $d.Name); type = "tool"; path = $d.FullName; source = "filesystem" })
        Log ("  FOUND: " + $d.FullName)
    }
} else {
    Log "  No graphify-out* directories found"
}

# NorthStar Ledger port
Log ""
Log "### NorthStar Ledger (port 3003)"
$ledgerConn = Get-NetTCPConnection -LocalPort 3003 -State Listen -ErrorAction SilentlyContinue
if ($ledgerConn) {
    $pid3003  = ($ledgerConn | Select-Object -First 1).OwningProcess
    $pname    = (Get-Process -Id $pid3003 -ErrorAction SilentlyContinue).ProcessName
    $found.Add(@{ name = "northstar-ledger"; type = "service"; path = "http://127.0.0.1:3003"; source = "port-scan" })
    Log ("  FOUND: listening on :3003 -- PID $pid3003 ($pname)")
} else {
    Log "  NOT FOUND: nothing listening on port 3003"
}

# Agent workspaces
Log ""
Log "### Agent Workspaces"
foreach ($agent in @("aristotle","daedalus","thales","steelman","researcher")) {
    $wsPath = "C:\Users\aaron\clawd-$agent"
    if (Test-Path $wsPath) {
        $found.Add(@{ name = ("workspace-" + $agent); type = "workspace"; path = $wsPath; source = "filesystem" })
        Log ("  FOUND: clawd-$agent -- $wsPath")
    } else {
        Log ("  NOT FOUND: clawd-$agent")
    }
}

# Build found name lookup
$foundNames = @{}
foreach ($f in $found) {
    $foundNames[$f.name.ToLower()] = $f
}

# STEP 3: Diff
Sep "Diff: Installed vs Registered"

if (-not $ledgerReachable) {
    Log "WARNING: Ledger was unreachable -- cannot compute diff. Re-run when ledger is online."
} else {
    # Installed but NOT in ledger
    Log ""
    Log "### Installed/Running but NOT Registered in Ledger"
    $unregistered = $found | Where-Object { -not $ledgerNames.ContainsKey($_.name.ToLower()) }
    if ($unregistered) {
        foreach ($u in $unregistered) {
            Log ("  UNREGISTERED: [" + $u.type + "] " + $u.name + " @ " + $u.path + " (via " + $u.source + ")")
        }
        Log ""
        Log "  ACTION: Register these with ledger-register.ps1 or document why excluded."
    } else {
        Log "  OK: All detected tools/services appear to be registered."
    }

    # Registered but NOT found
    Log ""
    Log "### Registered in Ledger but NOT Found on Machine"
    $missingItems = $ledgerResources | Where-Object {
        $n = if ($_.name) { $_.name.ToLower() } else { "" }
        $n -and (-not $foundNames.ContainsKey($n))
    }
    if ($missingItems) {
        foreach ($m in $missingItems) {
            $mname = if ($m.name) { $m.name } else { $m.id }
            $mpath = if ($m.path) { $m.path } elseif ($m.url) { $m.url } else { "(no path)" }
            Log ("  MISSING: [" + $m.type + "] $mname @ $mpath")
        }
        Log ""
        Log "  ACTION: Verify still in use. Remove stale ledger entries or reinstall missing tools."
    } else {
        Log "  OK: All registered resources appear to be present."
    }
}

# STEP 4: Summary
Sep "Summary"
Log ("Ledger reachable : " + $ledgerReachable)
Log ("Ledger resources : " + $ledgerResources.Count)
Log ("Detected locally : " + $found.Count)
if ($ledgerReachable) {
    $uCount = ($found | Where-Object { -not $ledgerNames.ContainsKey($_.name.ToLower()) }).Count
    $mCount = ($ledgerResources | Where-Object {
        $n = if ($_.name) { $_.name.ToLower() } else { "" }
        $n -and (-not $foundNames.ContainsKey($n))
    }).Count
    Log ("Unregistered     : $uCount  <- need ledger entries")
    Log ("Missing          : $mCount  <- registered but not found")
}
Log ""
Log "Run ledger-register.ps1 to register missing items."
Log "Audit complete."

# Optional file output
if ($OutputFile) {
    $lines | Out-File -FilePath $OutputFile -Encoding utf8
    Write-Host ""
    Write-Host ("Report written to: " + $OutputFile)
}
