from pydantic import BaseModel
from typing import List, Optional

class AuditorRequestCreate(BaseModel):
    company_name: str
    title: str
    category: str
    priority: str
    due_date: str
    description: str

class AuditorRequestSchema(BaseModel):
    id: str
    reference_code: str
    company_name: str
    title: str
    description: str
    category: str
    priority: str
    due_date: str
    status: str
    requested_by: str

class AttachedFileSchema(BaseModel):
    name: str
    size: str
    type: str
    download_url: Optional[str] = None

class ClientResponseSchema(BaseModel):
    id: str
    requestId: str
    requestTitle: str
    reference_code: Optional[str] = None
    companyName: str
    clientResponseNote: str
    submittedBy: str
    status: str # "unreviewed", "resolved", "revision_requested"
    submittedAt: str
    attachedFiles: List[AttachedFileSchema]

class AuditorResponsesSummary(BaseModel):
    totalResponses: int
    unreviewedCount: int
    responses: List[ClientResponseSchema]

class RevisionRequestNote(BaseModel):
    note: str
