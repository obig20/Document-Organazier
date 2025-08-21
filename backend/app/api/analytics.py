"""
Analytics endpoints
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalyticsResponse
from app.services.database.database import Database


router = APIRouter()
db = Database()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
	try:
		stats = db.get_feedback_stats()
		improvements = []
		for cat, acc in stats.get("by_category_accuracy", {}).items():
			if acc < 0.7:
				improvements.append(f"Improve training data for category '{cat}'")
		return AnalyticsResponse(
			total_feedback=stats.get("total_feedback", 0),
			accuracy=round(stats.get("accuracy", 0.0), 3),
			by_category_accuracy={k: round(v, 3) for k, v in stats.get("by_category_accuracy", {}).items()},
			improvement_opportunities=improvements,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


