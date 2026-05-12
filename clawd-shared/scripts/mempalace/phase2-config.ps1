$ErrorActionPreference = 'Stop'

$venv = 'C:\Users\aaron\mempalace-venv'
$py = Join-Path $venv 'Scripts\python.exe'

$env:PYTHONIOENCODING = 'utf-8'

# Identity file
$mpHome = 'C:\Users\aaron\.mempalace'
New-Item -ItemType Directory -Force -Path $mpHome | Out-Null

$identity = @'
Name: Aristotle
Role: CEO & Strategic Coordinator of AI agent family on Omni-AlienWare2025
Team: Daedalus (engineer), Thales (ops), Steel Man (critic), Researcher (analysis)
Owner: Aaron Baker
Primary Systems: NorthStar OS, OpenClaw, OmniPools Calculator
'@
$identityPath = Join-Path $mpHome 'identity.txt'
$identity | Out-File -Encoding utf8 $identityPath
Write-Host "Wrote identity: $identityPath"

# Wings: write mempalace.yaml into each root
function Write-WingYaml($root, $wing, $rooms) {
  if (-not (Test-Path $root)) {
    Write-Warning "Wing root missing, skipping: $root"
    return
  }
  $yamlPath = Join-Path $root 'mempalace.yaml'
  $lines = @()
  $lines += "wing: $wing"
  $lines += "rooms:"
  foreach ($r in $rooms) {
    $lines += "  - name: $($r.name)"
    $lines += "    description: $($r.description)"
  }
  # Security amendment: explicitly disable hooks (even if not required)
  $lines += "hooks: []"

  $lines -join "`n" | Out-File -Encoding utf8 $yamlPath
  Write-Host "Wrote $yamlPath"
}

Write-WingYaml 'C:\Users\aaron\clawd-aristotle' 'aristotle' @(
  @{ name='memory'; description='Daily logs, decisions, ongoing context' },
  @{ name='projects'; description='Project files, plans, specs' },
  @{ name='state'; description='State tracking and operational notes' },
  @{ name='general'; description='Everything else in the workspace' }
)

Write-WingYaml 'C:\Users\aaron\clawd-shared' 'shared' @(
  @{ name='specs'; description='Specifications, SOPs, handoffs' },
  @{ name='research'; description='Research outputs and briefs' },
  @{ name='governed-objects'; description='Canonical governed artifacts' },
  @{ name='tasks'; description='Task queue and runbooks' },
  @{ name='general'; description='Other shared workspace files' }
)

Write-WingYaml 'C:\North_Star_Projects' 'northstar' @(
  @{ name='docs'; description='Docs and notes' },
  @{ name='specs'; description='Specs and plans' },
  @{ name='general'; description='Everything else (curated before mining)' }
)

Write-WingYaml 'C:\Users\aaron\clawd-daedalus' 'daedalus' @(
  @{ name='memory'; description='Daily logs and notes' },
  @{ name='projects'; description='Project files' },
  @{ name='general'; description='Everything else' }
)

Write-WingYaml 'C:\Users\aaron\clawd-thales' 'thales' @(
  @{ name='memory'; description='Daily ops logs and notes' },
  @{ name='general'; description='Everything else in ops workspace' }
)

Write-WingYaml 'C:\Users\aaron\clawd-steelman' 'steelman' @(
  @{ name='memory'; description='Critical reviews and notes' },
  @{ name='general'; description='Everything else' }
)

Write-WingYaml 'C:\Users\aaron\clawd-researcher' 'researcher' @(
  @{ name='memory'; description='Research logs' },
  @{ name='general'; description='Everything else' }
)

# Claude export wing config (write file if root exists; mining is last)
Write-WingYaml 'C:\Users\Aaron\clawd\tmp\claude-sessions' 'claude-export' @(
  @{ name='convos'; description='Claude sessions (converted to per-session files)' }
)
Write-WingYaml 'C:\Users\Aaron\Downloads\Claude-Export' 'claude-export' @(
  @{ name='convos'; description='Claude export JSON (to be split/converted)' }
)

# Show mempalace status and mcp_server help for later documentation
& $py -m mempalace status
& $py -m mempalace.mcp_server --help | Out-File -Encoding utf8 (Join-Path $mpHome 'mcp_server-help.txt')

Write-Host 'Phase 2 complete.'
