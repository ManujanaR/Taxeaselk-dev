from pydantic import BaseModel
from typing import List, Optional

class DocumentRow(BaseModel):
    id: str
    name: str
    type: str
    status: str # "processing", "processed", "review_required", "verified"
    aiConfidencePercent: float
    uploadedDate: str
    sizeLabel: str

class DocumentsSummary(BaseModel):
    uploadedCount: int
    processedCount: int
    reviewRequiredCount: int
    missingCount: int
    documents: List[DocumentRow]

class DocumentUploadResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    ai_confidence_percent: float
    uploaded_date: str
    size_label: str
    file_url: Optional[str] = None
