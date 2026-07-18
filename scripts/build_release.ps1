param(
    [string]$Version = "0.1.2"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Create .venv and install the project before building the release."
}

Push-Location (Join-Path $Root "frontend")
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed with exit code $LASTEXITCODE." }
    npm test
    if ($LASTEXITCODE -ne 0) { throw "npm test failed with exit code $LASTEXITCODE." }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm build failed with exit code $LASTEXITCODE." }
} finally {
    Pop-Location
}

& $Python -m pytest
if ($LASTEXITCODE -ne 0) { throw "pytest failed with exit code $LASTEXITCODE." }
& $Python -m pip install -e "${Root}[package]"
if ($LASTEXITCODE -ne 0) { throw "package dependency install failed with exit code $LASTEXITCODE." }
Push-Location $Root
try {
    & $Python -m PyInstaller --noconfirm --clean .\MoEAutopilotStudio.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE." }
    $Zip = Join-Path $Root "dist\MoEAutopilotStudio-$Version-win-x64.zip"
    if (Test-Path -LiteralPath $Zip) {
        Remove-Item -LiteralPath $Zip
    }
    Compress-Archive -Path ".\dist\MoEAutopilotStudio\*" -DestinationPath $Zip -CompressionLevel Optimal
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Zip).Hash.ToLowerInvariant()
    Set-Content -LiteralPath "$Zip.sha256" -Value "$Hash  $(Split-Path -Leaf $Zip)" -Encoding ascii
    Write-Host "Release: $Zip"
    Write-Host "SHA-256: $Hash"
} finally {
    Pop-Location
}
