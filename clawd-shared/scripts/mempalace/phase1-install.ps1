$ErrorActionPreference = 'Stop'

$venv = 'C:\Users\aaron\mempalace-venv'

if (-not (Test-Path $venv)) {
  Write-Host "Creating venv at $venv"
  python -m venv $venv
} else {
  Write-Host "Venv already exists at $venv"
}

$py = Join-Path $venv 'Scripts\python.exe'

& $py -V
& $py -m pip install --upgrade pip

$env:PYTHONIOENCODING = 'utf-8'
& $py -m pip install mempalace==3.0.0

& $py -m pip freeze | Out-File -Encoding utf8 "$venv\requirements.lock.txt"

# Reproducibility mirrors
$mirrorDir = 'C:\Users\aaron\clawd-shared\source-mirrors\mempalace-3.0.0'
New-Item -ItemType Directory -Force -Path $mirrorDir | Out-Null
Copy-Item -Force "$venv\requirements.lock.txt" (Join-Path $mirrorDir 'requirements.lock.txt')

# Download wheel/sdist explicitly (pip cache path is unreliable)
& $py -m pip download --no-deps --dest $mirrorDir mempalace==3.0.0

# Verify install
$env:PYTHONIOENCODING = 'utf-8'
& $py -m mempalace --help | Out-File -Encoding utf8 (Join-Path $mirrorDir 'mempalace-help.txt')
& $py -m mempalace --help

Write-Host 'Phase 1 complete.'
