# ============================================================
# clawd-shared-sync.ps1 - Hourly bidirectional sync of clawd-shared
# Created: 2026-05-12 by Claude Opus 4.7 with Aaron
# Stagger: Aristotle :00 | Plato :20 | Empiricus :40
# Precedence: Aristotle (rank 1) > Plato (rank 2) > Empiricus (rank 3)
# Silent on success. Bridge alerts only on conflicts and real failures.
# ============================================================

$ErrorActionPreference = "Continue"

# --- PER-MACHINE CONFIG (CHANGE FOR EACH AGENT) ---------------
$AGENT_NAME = "empiricus"
$AGENT_RANK = 3

# --- COMMON CONFIG --------------------------------------------
$LOCAL_DIR     = "C:\Users\aaron\clawd-shared"
$REPO_DIR      = "C:\Users\aaron\github\family-backup"
$REPO_SUBDIR   = "clawd-shared"
$GH_TOKEN      = "[REDACTED_GH_CLASSIC]"
$REPO_URL      = "https://$GH_TOKEN@github.com/Nietzsche247/family-backup.git"
$BRIDGE_URL    = "http://100.108.47.36:3001/api/bridge/message"
$LOG_FILE      = "C:\Users\aaron\.openclaw\logs\clawd-shared-sync.log"
$STATE_FILE    = "C:\Users\aaron\.openclaw\logs\clawd-shared-sync.state.json"
$GIT_EXE       = "C:\Program Files\Git\bin\git.exe"
$ISO_TS        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$READABLE_TS   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# --- ALLOWLIST + EXCLUSIONS -----------------------------------
$ALLOWED_EXT = @('.md','.py','.cmd','.bat','.ps1','.txt','.json','.yaml','.yml','.toml','.cfg','.ini','.sh')

$EXCLUDED_SUBDIRS = @(
    'openclaw-fork','.tmp.driveupload','graft-analysis','me[REDACTED_MEM0_KEY]',
    'graphify-out-omnipools','backups','sync-to-plato-2026-05-11','.git',
    'omnipools-repo','omnipools-src','specs','source-mirrors','prodbx-docs',
    'buildertrend-docs','infranodus-snapshots','research','p1rails','p1verify',
    '_smoke-test','ssh-keys','recovery-keys','__pycache__','node_modules'
)

$EXCLUDED_FILENAMES = @('.env','[REDACTED_XAI_KEY].env','*.zip','*.xlsx','*.pdf','*.docx',
    '*.png','*.jpg','*.jpeg','*.gif','*.mp4','*.db','*.sqlite','*.sqlite3')

$MAX_FILE_SIZE_MB = 5

# --- SECRET PATTERNS (mirror daily-backup.ps1) ----------------
$SECRET_PATTERNS = @(
    @{P='sk-proj-[A-Za-z0-9_\-]+';      L='OPENAI_KEY'},
    @{P='sk-ant-[A-Za-z0-9_\-]+';       L='ANTHROPIC_KEY'},
    @{P='xai-[A-Za-z0-9_\-]+';          L='XAI_KEY'},
    @{P='AIzaSy[A-Za-z0-9_\-]+';        L='GOOGLE_KEY'},
    @{P='ghp_[A-Za-z0-9]+';             L='GH_CLASSIC'},
    @{P='github_pat_[A-Za-z0-9_\-]+';   L='GH_FINEGRAINED'},
    @{P='m0-[A-Za-z0-9_\-]+';           L='MEM0_KEY'},
    @{P='tvly-[A-Za-z0-9_\-]+';         L='TAVILY_KEY'},
    @{P='xoxb-[A-Za-z0-9_\-]+';         L='SLACK_BOT'},
    @{P='xapp-[A-Za-z0-9_\-]+';         L='SLACK_APP'}
)


# --- HELPERS --------------------------------------------------
function Write-SyncLog {
    param([string]$Level, [string]$Msg)
    Add-Content -Path $LOG_FILE -Value "[$ISO_TS] [$Level] $Msg" -ErrorAction SilentlyContinue
}

function Send-BridgeAlert {
    param([string]$Body)
    try {
        $payload = @{ from="clawd-shared-sync"; to="aristotle"; body="[$AGENT_NAME] $Body"; priority="normal" } | ConvertTo-Json
        Invoke-RestMethod -Uri $BRIDGE_URL -Method POST -Body $payload -ContentType "application/json" -TimeoutSec 5 | Out-Null
    } catch {
        Write-SyncLog "WARN" "Bridge alert failed (alert text: $Body)"
    }
}

function Run-Git {
    # Calls git via Start-Process to sidestep PowerShell pipeline parser bugs.
    # Returns combined stdout+stderr as strings. Sets $LASTEXITCODE.
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$GitArguments)
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    try {
        $cwd = (Get-Location).Path
        $p = Start-Process -FilePath $GIT_EXE -ArgumentList $GitArguments -WorkingDirectory $cwd `
             -NoNewWindow -Wait -PassThru `
             -RedirectStandardOutput $outFile -RedirectStandardError $errFile
        $global:LASTEXITCODE = $p.ExitCode
        Get-Content $outFile -ErrorAction SilentlyContinue
        Get-Content $errFile -ErrorAction SilentlyContinue
    } finally {
        Remove-Item $outFile -ErrorAction SilentlyContinue
        Remove-Item $errFile -ErrorAction SilentlyContinue
    }
}

function Scrub-Secrets {
    param([string]$Content)
    if (-not $Content) { return $Content }
    foreach ($e in $SECRET_PATTERNS) {
        $Content = $Content -replace $e.P, "[REDACTED_$($e.L)]"
    }
    return $Content
}

function Should-IncludeFile {
    param([string]$RelativePath)
    $segments = $RelativePath -split '[\\/]'
    $topDir = $segments[0]
    if ($EXCLUDED_SUBDIRS -contains $topDir) { return $false }
    $fileName = $segments[-1]
    foreach ($pat in $EXCLUDED_FILENAMES) { if ($fileName -like $pat) { return $false } }
    $ext = [System.IO.Path]::GetExtension($fileName).ToLower()
    if ($ALLOWED_EXT -contains $ext) { return $true }
    if ($segments.Count -eq 1 -and -not $ext) { return $true }
    return $false
}

function Get-RelPath {
    param([string]$FullPath, [string]$BasePath)
    $b = (Resolve-Path $BasePath).Path.TrimEnd('\','/')
    $f = $FullPath.TrimEnd('\','/')
    if ($f.StartsWith($b, [StringComparison]::OrdinalIgnoreCase)) {
        return $f.Substring($b.Length).TrimStart('\','/')
    }
    return $null
}

function Copy-WithScrub {
    param([string]$Src, [string]$Dst)
    $parent = Split-Path $Dst
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $content = Get-Content -Path $Src -Raw -ErrorAction SilentlyContinue
    if ($content) {
        $scrubbed = Scrub-Secrets $content
        Set-Content -Path $Dst -Value $scrubbed -NoNewline
    } else {
        Copy-Item -Path $Src -Destination $Dst -Force
    }
}

function Get-SyncState {
    if (Test-Path $STATE_FILE) {
        try {
            $obj = Get-Content $STATE_FILE -Raw | ConvertFrom-Json
            $h = @{}
            $obj.fileHashes.PSObject.Properties | ForEach-Object { $h[$_.Name] = $_.Value }
            return @{ fileHashes = $h; lastSync = $obj.lastSync }
        } catch { return @{ fileHashes = @{}; lastSync = $null } }
    }
    return @{ fileHashes = @{}; lastSync = $null }
}

function Save-SyncState {
    $repoBase = Join-Path $REPO_DIR $REPO_SUBDIR
    $hashes = @{}
    Get-ChildItem -Path $repoBase -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = Get-RelPath -FullPath $_.FullName -BasePath $repoBase
        if ($rel -and $rel -notmatch '\.conflict-[a-z]+-\d') {
            $hashes[$rel] = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        }
    }
    @{ fileHashes=$hashes; lastSync=$ISO_TS; agent=$AGENT_NAME } | ConvertTo-Json -Depth 4 | Set-Content $STATE_FILE
}


# --- GIT OPERATIONS -------------------------------------------
function Ensure-WorkingCopy {
    $parent = Split-Path $REPO_DIR
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }

    if (-not (Test-Path (Join-Path $REPO_DIR ".git"))) {
        Write-SyncLog "INFO" "Cloning family-backup..."
        if (Test-Path $REPO_DIR) { Remove-Item -Recurse -Force $REPO_DIR }
        Run-Git clone $REPO_URL $REPO_DIR 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Send-BridgeAlert "Initial clone of family-backup FAILED. Sync cannot proceed."
            throw "git clone failed"
        }
    }

    Push-Location $REPO_DIR
    try {
        Run-Git config user.email "$AGENT_NAME@northstar.local" 2>&1 | Out-Null
        Run-Git config user.name  "$AGENT_NAME-sync" 2>&1 | Out-Null
        # L37: Aaron's global git config has commit.gpgsign=true with SSH-key signing.
        # Non-interactive scheduled-task context cannot unlock the SSH key, which
        # causes "fatal: failed to write commit object". Disable signing locally
        # so this repo's commits don't require an interactive SSH key unlock.
        # Self-heals on every run -- safe to leave permanently.
        Run-Git config commit.gpgsign false 2>&1 | Out-Null
        Run-Git config tag.gpgsign    false 2>&1 | Out-Null
        Run-Git fetch origin main 2>&1 | Out-Null
        $localHead  = (Run-Git rev-parse HEAD 2>$null)
        $remoteHead = (Run-Git rev-parse origin/main 2>$null)
        if ($localHead -ne $remoteHead) {
            Run-Git reset --hard origin/main 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Send-BridgeAlert "git reset --hard origin/main FAILED. Investigate working copy at $REPO_DIR"
                throw "reset failed"
            }
            Write-SyncLog "INFO" "Reset to origin/main ($remoteHead)"
        }
    } finally { Pop-Location }

    $subdirPath = Join-Path $REPO_DIR $REPO_SUBDIR
    if (-not (Test-Path $subdirPath)) {
        New-Item -ItemType Directory -Force -Path $subdirPath | Out-Null
    }
}

function Commit-And-Push {
    Push-Location $REPO_DIR
    try {
        $changes = Run-Git status --porcelain
        if (-not $changes) { return $false }
        Run-Git add -A | Out-Null

        # Write commit message to a file to avoid Start-Process splitting args on spaces
        $msgFile = [System.IO.Path]::GetTempFileName()
        try {
            Set-Content -Path $msgFile -Value "auto: $AGENT_NAME sync $READABLE_TS"
            Run-Git commit -F $msgFile | Out-Null
        } finally {
            Remove-Item $msgFile -ErrorAction SilentlyContinue
        }

        Run-Git push origin main | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-SyncLog "WARN" "Push failed; one retry"
            Run-Git fetch origin main | Out-Null
            Run-Git pull --rebase origin main | Out-Null
            Run-Git push origin main | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Send-BridgeAlert "git push FAILED twice. Manual investigation needed at $REPO_DIR"
                throw "push failed twice"
            }
        }
        return $true
    } finally { Pop-Location }
}

function Mirror-CommsHubData {
    # One-directional mirror of comms-hub data dir (C:\bravo-team\) to repo/comms-hub-data/.
    # Only Aristotle (rank 1) runs this - that's where the canonical comms-hub server lives.
    # Used for off-site readable access to signal-fire, reports, and state files.
    $stats = @{ pushed = 0; skipped = 0 }

    if (-not (Test-Path "C:\bravo-team")) {
        Write-SyncLog "INFO" "No bravo-team dir on this machine, skipping comms-hub mirror"
        return $stats
    }

    $mirrorTargetBase = Join-Path $REPO_DIR "comms-hub-data"
    if (-not (Test-Path $mirrorTargetBase)) {
        New-Item -ItemType Directory -Force -Path $mirrorTargetBase | Out-Null
    }

    # Sources: local path -> repo subdir under comms-hub-data/
    $sources = @(
        @{ Local = "C:\bravo-team\signal-fire"; Repo = "signal-fire"; Recurse = $true  },
        @{ Local = "C:\bravo-team\reports";     Repo = "reports";     Recurse = $true  },
        @{ Local = "C:\bravo-team\state";       Repo = "state";       Recurse = $false }  # only top-level YAML
    )

    foreach ($src in $sources) {
        if (-not (Test-Path $src.Local)) { continue }
        $repoSubPath = Join-Path $mirrorTargetBase $src.Repo
        if (-not (Test-Path $repoSubPath)) { New-Item -ItemType Directory -Force -Path $repoSubPath | Out-Null }

        $params = @{ Path = $src.Local; File = $true; Force = $true; ErrorAction = "SilentlyContinue" }
        if ($src.Recurse) { $params.Recurse = $true }

        Get-ChildItem @params | ForEach-Object {
            $file = $_
            # Apply size limit and exclusion rules
            if (($file.Length / 1MB) -gt $MAX_FILE_SIZE_MB) {
                Write-SyncLog "WARN" "Mirror skip oversized $([math]::Round($file.Length/1MB,1))MB: $($file.FullName)"
                return
            }
            $fileName = $file.Name
            $skip = $false
            foreach ($pat in $EXCLUDED_FILENAMES) { if ($fileName -like $pat) { $skip = $true; break } }
            if ($skip) { return }

            # Allow JSON for signal-fire (each entry is a JSON file), MD for reports, YAML for state
            $ext = $file.Extension.ToLower()
            $allowed = @('.json', '.md', '.yaml', '.yml', '.txt')
            if ($ext -and $allowed -notcontains $ext) { return }

            # Compute relative path within the source root for target placement
            $relPath = $file.FullName.Substring($src.Local.Length).TrimStart('\','/')
            $targetPath = Join-Path $repoSubPath $relPath
            $targetParent = Split-Path $targetPath
            if (-not (Test-Path $targetParent)) { New-Item -ItemType Directory -Force -Path $targetParent | Out-Null }

            # Compare hashes to avoid touching unchanged files
            $needsCopy = $true
            if (Test-Path $targetPath) {
                $srcHash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
                $dstHash = (Get-FileHash $targetPath  -Algorithm SHA256).Hash
                if ($srcHash -eq $dstHash) { $needsCopy = $false }
            }

            if ($needsCopy) {
                Copy-WithScrub -Src $file.FullName -Dst $targetPath
                $stats.pushed++
            } else {
                $stats.skipped++
            }
        }
    }

    Write-SyncLog "INFO" "comms-hub mirror: pushed=$($stats.pushed) skipped=$($stats.skipped)"
    return $stats
}


# --- TWO-WAY FILE SYNC ----------------------------------------
function Sync-Files {
    $localBase = $LOCAL_DIR
    $repoBase  = Join-Path $REPO_DIR $REPO_SUBDIR

    $localFiles = @{}
    $repoFiles  = @{}

    Get-ChildItem -Path $localBase -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = Get-RelPath -FullPath $_.FullName -BasePath $localBase
        if ($rel -and (Should-IncludeFile $rel)) {
            if (($_.Length / 1MB) -le $MAX_FILE_SIZE_MB) {
                $localFiles[$rel] = $_
            } else {
                Write-SyncLog "WARN" "Skip oversized ($([math]::Round($_.Length/1MB,1)) MB): $rel"
            }
        }
    }

    Get-ChildItem -Path $repoBase -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = Get-RelPath -FullPath $_.FullName -BasePath $repoBase
        if ($rel -and ($rel -notmatch '\.conflict-[a-z]+-\d')) {
            $repoFiles[$rel] = $_
        }
    }

    $stats = @{ pushed=0; pulled=0; conflicts=0; skipped=0; sidecarsCleaned=0 }
    $state = Get-SyncState

    $allPaths = @($localFiles.Keys) + @($repoFiles.Keys) | Sort-Object -Unique

    foreach ($rel in $allPaths) {
        $local = $localFiles[$rel]
        $repo  = $repoFiles[$rel]
        $localPath = Join-Path $localBase $rel
        $repoPath  = Join-Path $repoBase  $rel

        if ($local -and -not $repo) {
            Copy-WithScrub -Src $localPath -Dst $repoPath
            $stats.pushed++
            continue
        }

        if ($repo -and -not $local) {
            $localParent = Split-Path $localPath
            if (-not (Test-Path $localParent)) { New-Item -ItemType Directory -Force -Path $localParent | Out-Null }
            Copy-Item -Path $repoPath -Destination $localPath -Force
            $stats.pulled++
            continue
        }

        # Both exist
        $localHash = (Get-FileHash $localPath -Algorithm SHA256).Hash
        $repoHash  = (Get-FileHash $repoPath  -Algorithm SHA256).Hash
        if ($localHash -eq $repoHash) { $stats.skipped++; continue }

        $lastSyncedHash = $state.fileHashes[$rel]
        $localChanged = ($localHash -ne $lastSyncedHash)
        $repoChanged  = ($repoHash  -ne $lastSyncedHash)

        if ($localChanged -and -not $repoChanged) {
            Copy-WithScrub -Src $localPath -Dst $repoPath
            $stats.pushed++
        }
        elseif ($repoChanged -and -not $localChanged) {
            Copy-Item -Path $repoPath -Destination $localPath -Force
            $stats.pulled++
        }
        else {
            # Genuine conflict
            $safeTs = $ISO_TS -replace ':', '-'
            if ($AGENT_RANK -eq 1) {
                # Aristotle wins. Save the incoming repo version as sidecar, push our local.
                $sidecarRel  = "$rel.conflict-remote-$safeTs"
                $sidecarPath = Join-Path $repoBase $sidecarRel
                $sp = Split-Path $sidecarPath
                if (-not (Test-Path $sp)) { New-Item -ItemType Directory -Force -Path $sp | Out-Null }
                Copy-Item -Path $repoPath -Destination $sidecarPath -Force
                Copy-WithScrub -Src $localPath -Dst $repoPath
                $stats.conflicts++
                Send-BridgeAlert "Conflict on '$rel' - Aristotle's local kept, prior remote saved as '$sidecarRel'"
            }
            else {
                # Plato/Empiricus: assume repo edit was higher-priority. Save our local as sidecar.
                $sidecarRel  = "$rel.conflict-$AGENT_NAME-$safeTs"
                $sidecarPath = Join-Path $repoBase $sidecarRel
                $sp = Split-Path $sidecarPath
                if (-not (Test-Path $sp)) { New-Item -ItemType Directory -Force -Path $sp | Out-Null }
                Copy-WithScrub -Src $localPath -Dst $sidecarPath
                Copy-Item -Path $repoPath -Destination $localPath -Force
                $stats.conflicts++
                Send-BridgeAlert "Conflict on '$rel' - $AGENT_NAME local preserved as '$sidecarRel', remote kept"
            }
        }
    }

    # Auto-clean sidecars older than 24h whose primary file is now in sync
    Get-ChildItem -Path $repoBase -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '\.conflict-[a-z]+-\d' } |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-24) } |
        ForEach-Object {
            $sideRel  = Get-RelPath -FullPath $_.FullName -BasePath $repoBase
            $primRel  = $sideRel -replace '\.conflict-[a-z]+-[\d\-T:Z]+$',''
            $primPath = Join-Path $repoBase $primRel
            if (Test-Path $primPath) {
                Remove-Item $_.FullName -Force
                $stats.sidecarsCleaned++
            }
        }

    return $stats
}


# --- MAIN -----------------------------------------------------
try {
    $logDir = Split-Path $LOG_FILE
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
    $env:Path = "C:\Program Files\Git\bin;$env:Path"

    Write-SyncLog "INFO" "=== sync start agent=$AGENT_NAME rank=$AGENT_RANK ==="

    Ensure-WorkingCopy
    $stats = Sync-Files

    # Aristotle is canonical for comms-hub data (lives at C:\bravo-team\ on her box).
    # One-directional mirror: local -> repo. Other ranks skip this.
    if ($AGENT_RANK -eq 1) {
        $mirrorStats = Mirror-CommsHubData
        $stats.pushed += $mirrorStats.pushed
    }

    $pushed = Commit-And-Push
    Save-SyncState

    $summary = "pushed=$($stats.pushed) pulled=$($stats.pulled) conflicts=$($stats.conflicts) skipped=$($stats.skipped) sidecarsCleaned=$($stats.sidecarsCleaned)"
    if ($stats.conflicts -gt 0) {
        Write-SyncLog "WARN" $summary
    } elseif ($pushed -or $stats.pulled -gt 0) {
        Write-SyncLog "INFO" $summary
    } else {
        Write-SyncLog "INFO" "no-op ($summary)"
    }
    Write-SyncLog "INFO" "=== sync complete ==="
} catch {
    $err = "Sync FAILED: $($_.Exception.Message)"
    Write-SyncLog "ERROR" $err
    # Don't alert on first-run failures (suppress noise during setup)
    if (Test-Path $STATE_FILE) {
        Send-BridgeAlert $err
    }
    exit 1
}
