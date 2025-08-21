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
		return AnalyticsResponse(
			total_feedback=stats.get("total_feedback", 0),
			overall_accuracy=round(stats.get("accuracy", 0.0), 3),
			category_accuracy={k: round(v, 3) for k, v in stats.get("by_category_accuracy", {}).items()},
			learning_potential=round(stats.get("learning_potential", 0.0), 3),
			recent_performance=stats.get("recent_performance", []),
			feedback_analysis=stats.get("feedback_analysis", {})
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


