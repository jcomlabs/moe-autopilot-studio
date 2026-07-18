param(
    [string]$Executable = "$PSScriptRoot\..\dist\MoEAutopilotStudio\MoEAutopilotStudio.exe",
    [int]$Port = 18765
)

$ErrorActionPreference = "Stop"
$Executable = (Resolve-Path -LiteralPath $Executable).Path
$env:STUDIO_OPEN_BROWSER = "0"
$env:STUDIO_PORT = [string]$Port
$Process = Start-Process -FilePath $Executable -WindowStyle Hidden -PassThru
try {
    $Deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 500
        try {
            $Health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
            if ($Health.status -eq "ok") {
                Write-Host "Packaged smoke passed on port $Port."
                exit 0
            }
        } catch {
        }
    } while ((Get-Date) -lt $Deadline -and -not $Process.HasExited)
    throw "Packaged Studio did not become healthy."
} finally {
    if (-not $Process.HasExited) {
        Stop-Process -Id $Process.Id
    }
}
