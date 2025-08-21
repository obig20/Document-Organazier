"""
Document service for handling document operations
"""
import asyncio
from typing import List, Optional
from pathlib import Path
import shutil
from fastapi.responses import FileResponse
from datetime import datetime

from app.models.document import Document
from app.models.schemas import (
    DocumentResponse, 
    DocumentDetail, 
    DocumentUpdate, 
    StatsResponse,
    DocumentStatus,
    DocumentMetadata
)
from app.services.database.database import Database
from app.services.processing.document_processor import DocumentProcessor
from app.services.ai.classifier import DocumentClassifier
from app.core.config import settings
from app.services.nlp.language import detect_language
from app.services.nlp.keyphrases import extract_key_phrases

class DocumentService:
    def __init__(self):
        self.db = Database()
        self.processor = DocumentProcessor()
        self.classifier = DocumentClassifier()
    
    async def create_document_record(self, filename: str, file_path: str) -> int:
        """Create initial document record in database"""
        document = Document(
            filename=filename,
            original_path=file_path,
            processing_status="pending"
        )
        return self.db.add_document(document)
    
    async def process_document_async(self, document_id: int, file_path: str):
        """Process document asynchronously"""
        try:
            # Update status to processing
            document = self.db.get_document(document_id)
            document.processing_status = "processing"
            self.db.update_document(document)
            
            # Process the document
            processed_doc, content = self.processor.process_document(file_path)
            
            # Classify the document
            category, confidence = self.classifier.classify_document(processed_doc)
            
            # Update document with results
            document.content = content
            document.category = category
            document.confidence_score = confidence
            document.is_processed = True
            document.processing_status = "completed"

            # Language detection and keyphrases
            language, lang_conf = detect_language(content)
            if document.metadata:
                document.metadata.language_detected = language
                document.metadata.ocr_confidence = lang_conf
            key_phrases = extract_key_phrases(content, top_k=10)
            document.tags = key_phrases[:5]
            
            # Move file to storage
            storage_path = Path(settings.STORAGE_DIR) / f"{document_id}_{document.filename}"
            shutil.move(file_path, storage_path)
            document.stored_path = str(storage_path)
            
            self.db.update_document(document)

            # Index to search service if available (best effort)
            try:
                from app.services.search_service import SearchService as ApiSearchService
                ApiSearchService().core_search.index_document(document)  # type: ignore[attr-defined]
            except Exception:
                pass
            
        except Exception as e:
            # Update document with error
            document = self.db.get_document(document_id)
            document.processing_status = "error"
            document.error_message = str(e)
            self.db.update_document(document)
            
            # Clean up temp file
            try:
                Path(file_path).unlink(missing_ok=True)
            except:
                pass
    
    async def get_documents(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[DocumentResponse]:
        """Get paginated list of documents"""
        # This would be implemented with proper database querying
        all_docs = self.db.get_all_documents()
        
        # Filter by category and status
        filtered_docs = []
        for doc in all_docs:
            if category and doc.category != category:
                continue
            if status and doc.processing_status != status:
                continue
            filtered_docs.append(doc)
        
        # Apply pagination
        paginated_docs = filtered_docs[skip:skip + limit]
        
        # Convert to response format
        return [self._document_to_response(doc) for doc in paginated_docs]
    
    async def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.get_document(document_id)
    
    async def get_document_detail(self, document_id: int) -> Optional[DocumentDetail]:
        """Get detailed document information"""
        document = self.db.get_document(document_id)
        if not document:
            return None
        
        return DocumentDetail(
            id=document.id,
            filename=document.filename,
            title=document.title or document.filename,
            category=document.category,
            confidence_score=document.confidence_score,
            tags=document.tags,
            created_date=document.created_date,
            updated_date=document.updated_date,
            is_processed=document.is_processed,
            processing_status=document.processing_status,
            content=document.content,
            error_message=document.error_message,
            metadata=self._metadata_to_response(document.metadata) if document.metadata else None
        )
    
    async def update_document(self, document_id: int, update_data: DocumentUpdate) -> Optional[DocumentResponse]:
        """Update document metadata"""
        document = self.db.get_document(document_id)
        if not document:
            return None
        
        if update_data.title is not None:
            document.title = update_data.title
        if update_data.category is not None:
            document.category = update_data.category.value
        if update_data.tags is not None:
            document.tags = update_data.tags
        
        document.updated_date = datetime.now()
        success = self.db.update_document(document)
        
        if success:
            return self._document_to_response(document)
        return None
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete document and its file"""
        document = self.db.get_document(document_id)
        if not document:
            return False
        
        # Delete file if exists
        if document.stored_path and Path(document.stored_path).exists():
            try:
                Path(document.stored_path).unlink()
            except:
                pass
        
        return self.db.delete_document(document_id)
    
    async def get_document_file(self, document_id: int) -> Optional[FileResponse]:
        """Get document file for download"""
        document = self.db.get_document(document_id)
        if not document or not document.stored_path:
            return None
        
        file_path = Path(document.stored_path)
        if not file_path.exists():
            return None
        
        return FileResponse(
            path=str(file_path),
            filename=document.filename,
            media_type='application/octet-stream'
        )
    
    async def get_statistics(self) -> StatsResponse:
        """Get system statistics"""
        # This would be implemented with proper database aggregation
        all_docs = self.db.get_all_documents()
        
        total_documents = len(all_docs)
        
        # Count by category
        categories = {}
        statuses = {}
        for doc in all_docs:
            categories[doc.category] = categories.get(doc.category, 0) + 1
            statuses[doc.processing_status] = statuses.get(doc.processing_status, 0) + 1
        
        # Calculate storage used (simplified)
        storage_used = 0
        try:
            for doc in all_docs:
                if doc.stored_path and Path(doc.stored_path).exists():
                    storage_used += Path(doc.stored_path).stat().st_size
        except:
            pass
        
        # Recent uploads (last 7 days)
        recent_uploads = sum(1 for doc in all_docs 
                           if (datetime.now() - doc.created_date).days <= 7)
        
        return StatsResponse(
            total_documents=total_documents,
            documents_by_category=categories,
            documents_by_status=statuses,
            storage_used_mb=round(storage_used / (1024 * 1024), 2),
            recent_uploads=recent_uploads
        )
    
    def _document_to_response(self, document: Document) -> DocumentResponse:
        """Convert Document to DocumentResponse"""
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            title=document.title or document.filename,
            category=document.category,
            confidence_score=document.confidence_score,
            tags=document.tags,
            created_date=document.created_date,
            updated_date=document.updated_date,
            is_processed=document.is_processed,
            processing_status=document.processing_status,
            content_preview=(document.content[:200] + "...") if document.content and len(document.content) > 200 else document.content,
            metadata=self._metadata_to_response(document.metadata) if document.metadata else None
        )
    
    def _metadata_to_response(self, metadata) -> DocumentMetadata:
        """Convert metadata to response format"""
        if not metadata:
            return None
            
        return DocumentMetadata(
            file_size=metadata.file_size,
            file_type=metadata.file_type,
            mime_type=metadata.mime_type,
            created_date=metadata.created_date,
            modified_date=metadata.modified_date,
            page_count=metadata.page_count,
            language_detected=metadata.language_detected,
            ocr_confidence=metadata.ocr_confidence
        )
