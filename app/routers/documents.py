import os, uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.schemas.document import DocumentsSummary, DocumentRow, DocumentUploadResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.get("", response_model=DocumentsSummary)
def get_documents_summary(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.company_name == company_name).all()
    uploaded = len(docs)
    processed = len([d for d in docs if d.status in ("processed", "verified")])
    review_req = len([d for d in docs if d.status == "review_required"])
    missing = max(0, 5 - uploaded)

    doc_rows = [
        DocumentRow(
            id=str(d.id),
            name=d.name,
            type=d.doc_type,
            status=d.status,
            aiConfidencePercent=d.ai_confidence_percent,
            uploadedDate=d.uploaded_date,
            sizeLabel=d.size_label
        ) for d in docs
    ]

    return DocumentsSummary(
        uploadedCount=uploaded,
        processedCount=processed,
        reviewRequiredCount=review_req,
        missingCount=missing,
        documents=doc_rows
    )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("Financial Statements"),
    company_name: str = Form("ABC (Pvt) Ltd"),
    db: Session = Depends(get_db)
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    meta = {"status": "uploaded", "ai_confidence_percent": None, "uploaded_date": "", "size_label": f"{os.path.getsize(file_path)/1024/1024:.1f} MB"}

    new_doc = Document(
        company_name=company_name,
        name=file.filename,
        file_url=f"/uploads/{saved_filename}",
        doc_type=doc_type,
        status=meta["status"],
        ai_confidence_percent=meta["ai_confidence_percent"],
        uploaded_date=meta["uploaded_date"],
        size_label=meta["size_label"]
    )
    db.add(new_doc)
    db.add(AuditLog(
        company_name=company_name,
        actor_name="Finance Team",
        actor_role="Company User",
        event_type="DOCUMENT_UPLOAD",
        details=f"Uploaded {file.filename} categorized under {doc_type}.",
        action_tone="success"
    ))
    db.commit()
    db.refresh(new_doc)

    return DocumentUploadResponse(
        id=str(new_doc.id),
        name=new_doc.name,
        type=new_doc.doc_type,
        status=new_doc.status,
        ai_confidence_percent=new_doc.ai_confidence_percent,
        uploaded_date=new_doc.uploaded_date,
        size_label=new_doc.size_label,
        file_url=new_doc.file_url
    )

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Document deleted successfully"}
