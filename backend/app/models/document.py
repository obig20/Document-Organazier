"""
Document data models for the AI Document Organizer
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass
class DocumentMetadata:
    """Metadata for a document"""
    file_size: int
    file_type: str
    mime_type: str
    created_date: datetime
    modified_date: datetime
    page_count: Optional[int] = None
    language_detected: Optional[str] = None
    ocr_confidence: Optional[float] = None

@dataclass
class DocumentTag:
    """Tag for document organization"""
    name: str
    color: str = "#1f77b4"
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class Document:
    """Main document model"""
    id: Optional[int] = None
    filename: str = ""
    original_path: str = ""
    stored_path: str = ""
    title: str = ""
    content: str = ""
    category: str = "other"
    confidence_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Optional[DocumentMetadata] = None
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    is_processed: bool = False
    processing_status: str = "pending"  # pending, processing, completed, error
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for storage"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_path': self.original_path,
            'stored_path': self.stored_path,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'confidence_score': self.confidence_score,
            'tags': json.dumps(self.tags),
            'metadata': json.dumps(self.metadata.__dict__ if self.metadata else {}),
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat(),
            'is_processed': self.is_processed,
            'processing_status': self.processing_status,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        metadata_dict = json.loads(data.get('metadata', '{}'))
        metadata = None
        if metadata_dict:
            metadata = DocumentMetadata(
                file_size=metadata_dict.get('file_size', 0),
                file_type=metadata_dict.get('file_type', ''),
                mime_type=metadata_dict.get('mime_type', ''),
                created_date=datetime.fromisoformat(metadata_dict.get('created_date', datetime.now().isoformat())),
                modified_date=datetime.fromisoformat(metadata_dict.get('modified_date', datetime.now().isoformat())),
                page_count=metadata_dict.get('page_count'),
                language_detected=metadata_dict.get('language_detected'),
                ocr_confidence=metadata_dict.get('ocr_confidence')
            )
        
        return cls(
            id=data.get('id'),
            filename=data.get('filename', ''),
            original_path=data.get('original_path', ''),
            stored_path=data.get('stored_path', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            category=data.get('category', 'other'),
            confidence_score=data.get('confidence_score', 0.0),
            tags=json.loads(data.get('tags', '[]')),
            metadata=metadata,
            created_date=datetime.fromisoformat(data.get('created_date', datetime.now().isoformat())),
            updated_date=datetime.fromisoformat(data.get('updated_date', datetime.now().isoformat())),
            is_processed=data.get('is_processed', False),
            processing_status=data.get('processing_status', 'pending'),
            error_message=data.get('error_message')
        )
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the document"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_date = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_date = datetime.now()
    
    def update_content(self, content: str) -> None:
        """Update document content"""
        self.content = content
        self.updated_date = datetime.now()
    
    def set_category(self, category: str, confidence: float = 0.0) -> None:
        """Set document category with confidence score"""
        self.category = category
        self.confidence_score = confidence
        self.updated_date = datetime.now()
    
    def mark_processed(self, status: str = "completed", error: Optional[str] = None) -> None:
        """Mark document as processed"""
        self.is_processed = status == "completed"
        self.processing_status = status
        self.error_message = error
        self.updated_date = datetime.now()

@dataclass
class SearchResult:
    """Search result model"""
    document: Document
    relevance_score: float
    matched_fields: List[str]
    snippet: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary"""
        return {
            'document': self.document.to_dict(),
            'relevance_score': self.relevance_score,
            'matched_fields': self.matched_fields,
            'snippet': self.snippet
        }
