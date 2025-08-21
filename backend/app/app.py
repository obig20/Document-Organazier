from fastapi import FastAPI

from app.api import health, upload, documents, search
try:
	from app.api import feedback, analytics
except Exception:
	feedback = None
	analytics = None


def create_app() -> FastAPI:
	app = FastAPI(title="AI Document Organizer API")
	app.include_router(health.router, prefix="/api/v1", tags=["health"])
	app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
	app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
	app.include_router(search.router, prefix="/api/v1", tags=["search"])
	if feedback:
		app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
	if analytics:
		app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
	return app


