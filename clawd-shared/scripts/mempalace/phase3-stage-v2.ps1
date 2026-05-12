$ErrorActionPreference = 'Stop'

$stagingRoot = 'C:\Users\aaron\mempalace-staging'
if (Test-Path $stagingRoot) {
  Write-Host "Removing prior staging at $stagingRoot"
  Remove-Item -Recurse -Force $stagingRoot
}
New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

# Steel Man exclusions
$excludeDirs = @(
  '.git','node_modules','dist','build','__pycache__','.venv','venv','.mempalace','.pytest_cache',
  'tmp','temp','logs','.clawdhub','.githooks','.idea','.vscode','coverage','.next','out','bin','obj'
)
$excludeFiles = @(
  '.env*','*secrets*','*secret*','*token*','*key*','*.pem','*.pfx','*.kdbx',
  'id_rsa*','known_hosts*','*cloudflared*','*credential*','*creds*'
)

# Conservative include list: docs + logs only
$includePatterns = @('*.md','*.txt')

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

    $p = Start-Process -FilePath $cmd[0] -ArgumentList ($cmd[1..($cmd.Length-1)]) -NoNewWindow -PassThru -Wait
    if ($p.ExitCode -ge 8) {
      throw "Robocopy failed ($($p.ExitCode)) staging $source -> $dest ($pat)"
    }
  }
}

# Batch 1 staging (Aristotle) — only the high-signal doc areas
Stage-Curated 'C:\Users\aaron\clawd-aristotle\memory'   (Join-Path $stagingRoot 'aristotle\memory')
Stage-Curated 'C:\Users\aaron\clawd-aristotle\projects' (Join-Path $stagingRoot 'aristotle\projects')
Stage-Curated 'C:\Users\aaron\clawd-aristotle\reviews'  (Join-Path $stagingRoot 'aristotle\reviews')

# Copy mempalace.yaml explicitly (safe)
Copy-Item -Force 'C:\Users\aaron\clawd-aristotle\mempalace.yaml' (Join-Path $stagingRoot 'aristotle\mempalace.yaml')

# Batch 2 staging (Shared)
Stage-Curated 'C:\Users\aaron\clawd-shared\specs'            (Join-Path $stagingRoot 'shared\specs')
Stage-Curated 'C:\Users\aaron\clawd-shared\research'          (Join-Path $stagingRoot 'shared\research')
Stage-Curated 'C:\Users\aaron\clawd-shared\governed-objects'  (Join-Path $stagingRoot 'shared\governed-objects')
Stage-Curated 'C:\Users\aaron\clawd-shared\tasks'             (Join-Path $stagingRoot 'shared\tasks')
Copy-Item -Force 'C:\Users\aaron\clawd-shared\mempalace.yaml' (Join-Path $stagingRoot 'shared\mempalace.yaml')

# Batch 3 staging (NorthStar)
Stage-Curated 'C:\North_Star_Projects' (Join-Path $stagingRoot 'northstar')
Copy-Item -Force 'C:\North_Star_Projects\mempalace.yaml' (Join-Path $stagingRoot 'northstar\mempalace.yaml')

Write-Host "Staging complete at: $stagingRoot"
