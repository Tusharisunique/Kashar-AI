from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from routes.auth import get_current_user
from services.document_service import document_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user = Depends(get_current_user)
):
    """Upload and process a document"""
    try:
        # Comprehensive file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Sanitize filename
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', file.filename)
        if not safe_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Validate file extension
        allowed_extensions = ['.pdf']
        if not any(safe_filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size
        if not file.size:
            raise HTTPException(status_code=400, detail="Empty file not allowed")
        
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed")
        
        # Validate content type
        allowed_content_types = ['application/pdf']
        if file.content_type not in allowed_content_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed")
        
        # Sanitize title
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="Document title is required")
        
        title = title.strip()[:200]  # Limit title length
        if len(title) < 1:
            raise HTTPException(status_code=400, detail="Document title cannot be empty")
        
        # Check for malicious content in title
        if any(char in title for char in ['<', '>', '"', "'", '&']):
            raise HTTPException(status_code=400, detail="Document title contains invalid characters")
        
        result = await document_service.upload_and_process_document(
            file=file,
            title=title,
            user_id=current_user.id
        )
        
        return {
            "message": "Document uploaded and processed successfully",
            "document": result
        }
        
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_documents(current_user = Depends(get_current_user)):
    """Get all documents for the current user"""
    try:
        documents = await document_service.get_user_documents(current_user.id)
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Get documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics")
async def get_topics(current_user = Depends(get_current_user)):
    """Get all topics for the current user"""
    try:
        topics = await document_service.get_user_topics(current_user.id)
        return {"topics": topics}
    except Exception as e:
        logger.error(f"Get topics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id, current_user.id)
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
