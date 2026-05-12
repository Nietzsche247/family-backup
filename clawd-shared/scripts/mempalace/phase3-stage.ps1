$ErrorActionPreference = 'Stop'

$stagingRoot = 'C:\Users\aaron\mempalace-staging'
New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

# Shared exclude patterns (Steel Man amendments)
$excludeDirs = @('.git','node_modules','dist','build','__pycache__','.venv','venv','.mempalace','.pytest_cache')
$excludeFiles = @(
  '.env*','*secrets*','*secret*','*token*','*key*','*.pem','*.pfx','*.kdbx',
  'id_rsa*','known_hosts*','*cloudflared*','*credential*','*creds*'
)

# Only copy these extensions (curated, high-signal)
$includePatterns = @('*.md','*.txt','*.yaml','*.yml')

function Stage-Curated($source, $dest) {
  if (-not (Test-Path $source)) {
    Write-Warning "Missing source: $source"
    return
  }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null

  foreach ($pat in $includePatterns) {
    $cmd = @(
      'robocopy',
      $source,
      $dest,
      $pat,
      '/S', '/R:1', '/W:1', '/NP',
      '/XD'
    ) + $excludeDirs + @('/XF') + $excludeFiles

    # Robocopy returns codes 0-7 as success; don't fail the script on those.
    $p = Start-Process -FilePath $cmd[0] -ArgumentList ($cmd[1..($cmd.Length-1)]) -NoNewWindow -PassThru -Wait
    if ($p.ExitCode -ge 8) {
      throw "Robocopy failed ($($p.ExitCode)) staging $source -> $dest ($pat)"
    }
  }
}

# Batch 1 staging (Aristotle)
Stage-Curated 'C:\Users\aaron\clawd-aristotle\memory'   (Join-Path $stagingRoot 'aristotle\memory')
Stage-Curated 'C:\Users\aaron\clawd-aristotle\projects' (Join-Path $stagingRoot 'aristotle\projects')
Stage-Curated 'C:\Users\aaron\clawd-aristotle'          (Join-Path $stagingRoot 'aristotle\root')

# Batch 2 staging (Shared)
Stage-Curated 'C:\Users\aaron\clawd-shared\specs'            (Join-Path $stagingRoot 'shared\specs')
Stage-Curated 'C:\Users\aaron\clawd-shared\research'          (Join-Path $stagingRoot 'shared\research')
Stage-Curated 'C:\Users\aaron\clawd-shared\governed-objects'  (Join-Path $stagingRoot 'shared\governed-objects')
Stage-Curated 'C:\Users\aaron\clawd-shared\tasks'             (Join-Path $stagingRoot 'shared\tasks')

# Batch 3 staging (NorthStar) — stage only docs/specs-like files from the whole tree
Stage-Curated 'C:\North_Star_Projects' (Join-Path $stagingRoot 'northstar')

Write-Host "Staging complete at: $stagingRoot"
