# Frontend Startup Script
Write-Host "Starting AI Document Organizer Frontend..." -ForegroundColor Green

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm not found. Please install npm and add it to PATH." -ForegroundColor Red
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Start the development server
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Make sure the backend is running on http://localhost:8000" -ForegroundColor Yellow

npm start
