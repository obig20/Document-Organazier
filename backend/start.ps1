# Backend Startup Script
Write-Host "Starting AI Document Organizer Backend..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
}

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Set Python path
$env:PYTHONPATH = $PWD

# Test backend components
Write-Host "Testing backend components..." -ForegroundColor Yellow
python test_backend.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend test passed!" -ForegroundColor Green
    Write-Host "Starting server..." -ForegroundColor Green
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    Write-Host "✗ Backend test failed. Check the errors above." -ForegroundColor Red
    exit 1
}
