"""
Document management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.schemas import (
    DocumentResponse, 
    DocumentDetail, 
    DocumentUpdate,
    DocumentCategory,
    StatsResponse
)
from app.services.document_service import DocumentService

router = APIRouter()
document_service = DocumentService()

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[DocumentCategory] = None,
    status: Optional[str] = None
):
    """Get list of documents with pagination and filtering"""
    try:
        documents = await document_service.get_documents(
            skip=skip,
            limit=limit,
            category=category.value if category else None,
            status=status
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: int):
    """Get detailed document information"""
    try:
        document = await document_service.get_document_detail(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: int, update_data: DocumentUpdate):
    """Update document metadata"""
    try:
        document = await document_service.update_document(document_id, update_data)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/download")
async def download_document(document_id: int):
    """Download original document file"""
    try:
        file_response = await document_service.get_document_file(document_id)
        if not file_response:
            raise HTTPException(status_code=404, detail="Document file not found")
        return file_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get system statistics"""
    try:
        stats = await document_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """Get available document categories"""
    return {
        "categories": [
            {"value": "demographics", "label": "Demographics", "description": "Personal and demographic documents"},
            {"value": "housing", "label": "Housing", "description": "Housing and property related documents"},
            {"value": "id_registry", "label": "ID Registry", "description": "Identity and registration documents"},
            {"value": "land_plans", "label": "Land Plans", "description": "Land ownership and planning documents"},
            {"value": "other", "label": "Other", "description": "Uncategorized documents"}
        ]
    }
