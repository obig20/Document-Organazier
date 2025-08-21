"""
Document upload and processing endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import shutil
import uuid
from pathlib import Path

from app.models.schemas import DocumentUploadResponse, DocumentStatus, DocumentProcessResponse
from app.services.document_service import DocumentService
from app.core.config import settings

router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=List[DocumentUploadResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload and process multiple documents"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    
    for file in files:
        # Validate file
        if not file.filename:
            continue
            
        # Size check is best-effort; UploadFile has no size attribute in FastAPI.
        # We'll enforce after saving by checking file size on disk.
        
        # Check file extension
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.txt'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            results.append(DocumentUploadResponse(
                document_id=0,
                filename=file.filename,
                status=DocumentStatus.ERROR,
                message=f"Unsupported file type: {file_ext}"
            ))
            continue
        
        try:
            # Save file temporarily
            file_id = str(uuid.uuid4())
            temp_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Enforce size limit after save
            try:
                if temp_path.stat().st_size > settings.MAX_FILE_SIZE:
                    temp_path.unlink(missing_ok=True)
                    results.append(DocumentUploadResponse(
                        document_id=0,
                        filename=file.filename,
                        status=DocumentStatus.ERROR,
                        message=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                    ))
                    continue
            except Exception:
                pass
            
            # Start processing in background
            document_id = await document_service.create_document_record(
                filename=file.filename,
                file_path=str(temp_path)
            )
            
            # Add background task for processing
            background_tasks.add_task(
                document_service.process_document_async,
                document_id,
                str(temp_path)
            )
            
            results.append(DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                status=DocumentStatus.PROCESSING,
                message="Document uploaded and processing started"
            ))
            
        except Exception as e:
            results.append(DocumentUploadResponse(
                document_id=0,
                filename=file.filename,
                status=DocumentStatus.ERROR,
                message=f"Upload failed: {str(e)}"
            ))
    
    return results

@router.post("/upload/process", response_model=DocumentProcessResponse)
async def upload_and_process_single(file: UploadFile = File(...)):
    """Upload and immediately process a single file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    allowed_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.txt'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    
    try:
        # Save file temporarily
        file_id = str(uuid.uuid4())
        temp_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Enforce size limit after save
        try:
            if temp_path.stat().st_size > settings.MAX_FILE_SIZE:
                temp_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
        except Exception:
            pass
        
        # Process immediately
        result = await document_service.process_document_sync(
            filename=file.filename,
            file_path=str(temp_path)
        )
        
        return result
        
    except Exception as e:
        # Clean up temp file
        try:
            temp_path.unlink(missing_ok=True)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/upload/status/{document_id}")
async def get_upload_status(document_id: int):
    """Get upload and processing status for a document"""
    try:
        document = document_service.db.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "status": document.processing_status,
            "filename": document.filename,
            "is_processed": document.is_processed,
            "error_message": document.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
