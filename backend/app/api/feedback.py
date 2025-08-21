"""
Feedback endpoints
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.services.database.database import Database


router = APIRouter()
db = Database()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
	try:
		# Validate document exists
		doc = db.get_document(payload.document_id)
		if not doc:
			raise HTTPException(status_code=404, detail="Document not found")

		correct_category = payload.correct_category.value if payload.correct_category else None
		db.add_feedback(payload.document_id, payload.was_correct, correct_category, payload.notes)
		return FeedbackResponse(success=True, message="Feedback recorded")
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


