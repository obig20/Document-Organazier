"""
Health check and system status endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import sys
import subprocess

from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health and dependencies"""
    dependencies = {}
    
    # Check Python version
    dependencies["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Check if Tesseract is available
    try:
        result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            dependencies["tesseract"] = version_line.split()[-1] if version_line else "unknown"
        else:
            dependencies["tesseract"] = "not available"
    except:
        dependencies["tesseract"] = "not available"
    
    # Check database connectivity
    try:
        from app.services.database.database import Database
        Database()  # initialization will create tables
        dependencies["database"] = "connected"
    except Exception as e:
        dependencies["database"] = f"error: {str(e)[:80]}"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        dependencies=dependencies
    )
