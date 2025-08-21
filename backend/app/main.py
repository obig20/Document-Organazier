"""
AI Document Organizer - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import documents, search, upload, health
from app.api import feedback, analytics
from app.core.config import settings


app = FastAPI(
	title="AI Document Organizer API",
	description="Advanced document organization with AI-powered classification and multilingual support",
	version="1.0.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:8080"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

app.mount("/static", StaticFiles(directory=str(settings.DATA_DIR / "storage")), name="static")

@app.get("/")
async def root():
	return {"message": "AI Document Organizer API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
	uvicorn.run(
		"app.main:app",
		host=settings.HOST,
		port=settings.PORT,
		reload=settings.DEBUG,
	)
