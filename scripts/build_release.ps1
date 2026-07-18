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
    npm test
    npm run build
} finally {
    Pop-Location
}

& $Python -m pytest
& $Python -m pip install -e "${Root}[package]"
Push-Location $Root
try {
    & $Python -m PyInstaller --noconfirm --clean .\MoEAutopilotStudio.spec
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
