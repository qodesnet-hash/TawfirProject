# verify_growth.ps1
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "       Merchant Growth Verification Tool       " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot activate virtual environment" -ForegroundColor Red
    Write-Host "Please make sure venv exists" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run verification
Write-Host ""
Write-Host "Running analytics verification..." -ForegroundColor Yellow
Write-Host ""

python verify_analytics.py

# Deactivate
deactivate

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
