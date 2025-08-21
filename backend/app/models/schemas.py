"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    ERROR = "error"

class DocumentCategory(str, Enum):
    DEMOGRAPHICS = "demographics"
    HOUSING = "housing"
    ID_REGISTRY = "id_registry"
    LAND_PLANS = "land_plans"
    OTHER = "other"

# Request Models
class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: int
    filename: str
    status: DocumentStatus
    message: str

class DocumentProcessResponse(BaseModel):
    """Response model for single file upload and processing"""
    document_id: int
    filename: str
    title: str
    category: DocumentCategory
    confidence_score: float
    language_detected: Optional[str] = None
    key_phrases: List[str] = []
    content_preview: Optional[str] = None
    processing_status: DocumentStatus
    message: str

class SearchRequest(BaseModel):
    """Request model for document search"""
    query: Optional[str] = None
    category: Optional[DocumentCategory] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=100)
    use_semantic: bool = True
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

class DocumentUpdate(BaseModel):
    """Request model for updating document"""
    title: Optional[str] = None
    category: Optional[DocumentCategory] = None
    tags: Optional[List[str]] = None

# Response Models
class DocumentMetadata(BaseModel):
    """Document metadata response"""
    file_size: int
    file_type: str
    mime_type: str
    created_date: datetime
    modified_date: datetime
    page_count: Optional[int] = None
    language_detected: Optional[str] = None
    ocr_confidence: Optional[float] = None

class DocumentResponse(BaseModel):
    """Document response model"""
    id: int
    filename: str
    title: str
    category: DocumentCategory
    confidence_score: float
    tags: List[str]
    created_date: datetime
    updated_date: datetime
    is_processed: bool
    processing_status: DocumentStatus
    metadata: Optional[DocumentMetadata] = None
    content_preview: Optional[str] = None  # First 200 chars of content

class DocumentDetail(DocumentResponse):
    """Detailed document response with full content"""
    content: str
    error_message: Optional[str] = None

class SearchResult(BaseModel):
    """Search result model"""
    document: DocumentResponse
    relevance_score: float
    matched_fields: List[str]
    snippet: str

class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    total_count: int
    query_time_ms: float
    search_params: SearchRequest

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    dependencies: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

class StatsResponse(BaseModel):
    """Statistics response"""
    total_documents: int
    documents_by_category: Dict[str, int]
    documents_by_status: Dict[str, int]
    storage_used_mb: float
    recent_uploads: int


class FeedbackRequest(BaseModel):
    """User feedback on classification"""
    document_id: int
    was_correct: bool
    correct_category: Optional[DocumentCategory] = None
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback acknowledgement"""
    success: bool
    message: str


class AnalyticsResponse(BaseModel):
    """Analytics for basic accuracy and trends"""
    total_feedback: int
    accuracy: float
    by_category_accuracy: Dict[str, float]
    improvement_opportunities: List[str]
