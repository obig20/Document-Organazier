"""
Search endpoints
"""
from fastapi import APIRouter, HTTPException
import time

from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()

@router.post("/search", response_model=SearchResponse)
async def search_documents(search_request: SearchRequest):
    """Search documents using keyword and semantic search"""
    try:
        start_time = time.time()
        
        results, total_count = await search_service.search(
            query=search_request.query,
            category=search_request.category.value if search_request.category else None,
            tags=search_request.tags,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            limit=search_request.limit,
            use_semantic=search_request.use_semantic,
            similarity_threshold=search_request.similarity_threshold
        )
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=results,
            total_count=total_count,
            query_time_ms=round(query_time_ms, 2),
            search_params=search_request
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/suggestions")
async def get_search_suggestions(q: str):
    """Get search suggestions based on query"""
    try:
        suggestions = await search_service.get_suggestions(q)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/recent")
async def get_recent_documents(limit: int = 10):
    """Get recently added documents"""
    try:
        results = await search_service.get_recent_documents(limit=limit)
        return {"results": results, "total_count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
