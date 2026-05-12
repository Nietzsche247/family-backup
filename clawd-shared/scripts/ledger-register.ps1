# ledger-register.ps1 -- NorthStar Ledger Registration Helper
# Reduces ledger registration from "hand-craft a JSON POST" to a one-liner.
#
# Usage:
#   .\ledger-register.ps1 -Name "tool-x" -Type tool -Path "/foo/bar" -Owner aristotle -Description "desc" -Tags "tag1,tag2"
#
# Parameters:
#   -Name        Required. Unique identifier for the resource.
#   -Type        Required. E.g.: tool, service, workspace, model, script, dataset
#   -Path        Required. Filesystem path or URL where the resource lives.
#   -Owner       Required. Which agent owns/registered this. E.g.: aristotle, daedalus, thales
#   -Description Optional. Human-readable description.
#   -Tags        Optional. Comma-separated tags. E.g.: "ai,memory,python"
#   -LedgerUrl   Optional. Defaults to http://127.0.0.1:3003
#   -DryRun      Optional. Print the payload without posting.

param(
    [Parameter(Mandatory=$true)]  [string]$Name,
    [Parameter(Mandatory=$true)]  [string]$Type,
    [Parameter(Mandatory=$true)]  [string]$Path,
    [Parameter(Mandatory=$true)]  [string]$Owner,
    [string]$Description = "",
    [string]$Tags        = "",
    [string]$LedgerUrl   = "http://127.0.0.1:3003",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Build payload
$tagArray = @()
if ($Tags) {
    $tagArray = $Tags -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

$payload = @{
    name        = $Name
    type        = $Type
    path        = $Path
    owner       = $Owner
    description = $Description
    tags        = $tagArray
    registered  = (Get-Date -Format "o")
    host        = $env:COMPUTERNAME
}

$json = $payload | ConvertTo-Json -Depth 5

# Dry-run preview
if ($DryRun) {
    Write-Host ("DRY RUN -- would POST to: " + $LedgerUrl + "/register")
    Write-Host ""
    Write-Host $json
    Write-Host ""
    Write-Host "No changes made."
    exit 0
}

# Post to ledger
Write-Host ("Registering '" + $Name + "' (" + $Type + ") with NorthStar Ledger...")

try {
    $response = Invoke-RestMethod `
        -Uri         ($LedgerUrl + "/register") `
        -Method      POST `
        -Body        $json `
        -ContentType "application/json" `
        -TimeoutSec  10 `
        -ErrorAction Stop

    Write-Host "Registered successfully."
    Write-Host ""
    Write-Host "Response:"
    Write-Host ($response | ConvertTo-Json -Depth 5)
} catch {
    $errMsg = $_.Exception.Message
    Write-Host ""
    Write-Host "Registration failed."
    Write-Host ("  Error: " + $errMsg)
    Write-Host ""
    Write-Host "Payload that was attempted:"
    Write-Host $json
    Write-Host ""
    Write-Host ("Is the ledger running? Test: Invoke-RestMethod " + $LedgerUrl + "/query")
    exit 1
}
