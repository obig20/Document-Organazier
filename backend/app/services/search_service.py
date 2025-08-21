"""
Search service adapter for API
"""
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.schemas import SearchResult, DocumentResponse
from app.services.ai.search_service import SearchService as CoreSearchService
from app.services.database.database import Database

class SearchService:
    def __init__(self):
        self.core_search = CoreSearchService()
        self.db = Database()
    
    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
        use_semantic: bool = True,
        similarity_threshold: float = 0.5
    ) -> Tuple[List[SearchResult], int]:
        """Search documents and return results"""
        
        # Fallback: use database LIKE search if core search fails
        try:
            core_results = self.core_search.search(
                query=query or "",
                category=category,
                tags=tags,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                use_semantic=use_semantic,
                similarity_threshold=similarity_threshold
            )

            results = []
            for result in core_results:
                document_response = DocumentResponse(
                    id=int(result.document_id),
                    filename=result.title,
                    title=result.title,
                    category=result.category,
                    confidence_score=result.score,
                    tags=[],
                    created_date=result.created_date,
                    updated_date=result.created_date,
                    is_processed=True,
                    processing_status="completed"
                )
                api_result = SearchResult(
                    document=document_response,
                    relevance_score=result.score,
                    matched_fields=["content", "title"],
                    snippet=result.snippet
                )
                results.append(api_result)
            return results, len(results)
        except Exception:
            results, total = self.db.search_documents(
                query=query or "",
                category=category,
                tags=tags or [],
                limit=limit,
                offset=0,
            )
            return results, total
    
    async def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions"""
        # This would implement autocomplete/suggestions
        # For now, return empty list
        return []
    
    async def get_recent_documents(self, limit: int = 10) -> List[DocumentResponse]:
        """Get recently added documents"""
        try:
            recent_results = self.core_search.get_recent_documents(limit=limit)
        except Exception:
            # Fallback: pull from DB
            docs = self.db.get_all_documents()[-limit:]
            from app.models.schemas import DocumentStatus as DS
            return [
                DocumentResponse(
                    id=d.id or 0,
                    filename=d.filename,
                    title=d.title or d.filename,
                    category=d.category,
                    confidence_score=d.confidence_score,
                    tags=d.tags,
                    created_date=d.created_date,
                    updated_date=d.updated_date,
                    is_processed=d.is_processed,
                    processing_status=DS(d.processing_status),
                    metadata=None,
                    content_preview=(d.content[:200] + '...') if d.content and len(d.content) > 200 else d.content,
                ) for d in docs
            ]
        
        results = []
        for result in recent_results:
            document_response = DocumentResponse(
                id=int(result.document_id),
                filename=result.title,
                title=result.title,
                category=result.category,
                confidence_score=result.score,
                tags=[],
                created_date=result.created_date,
                updated_date=result.created_date,
                is_processed=True,
                processing_status="completed"
            )
            results.append(document_response)
        
        return results
