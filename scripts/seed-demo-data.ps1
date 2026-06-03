$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Seeder = Join-Path $PSScriptRoot "seed-demo-data.py"

if (-not (Test-Path $Python)) {
    throw "Python venv not found at $Python"
}

Push-Location $ProjectRoot
try {
    & $Python $Seeder
}
finally {
    Pop-Location
}
