from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AuditorReviewIssueSchema(BaseModel):
    id: str
    status: str # "action_required", "pending_clarification", "resolved"
    severity: str # "critical", "warning"
    title: str
    comment: str
    source: str
    response_text: Optional[str] = None
    attached_file_name: Optional[str] = None

class AuditorReviewSummary(BaseModel):
    auditorName: str
    auditorFirm: str
    auditorEmail: str
    reviewStatus: str
    submittedDate: str
    expectedByDate: str
    reviewedPercent: int
    approvedCount: int
    warningsCount: int
    criticalCount: int
    pendingCount: int
    issues: List[AuditorReviewIssueSchema]

class IssueRespondRequest(BaseModel):
    response: str
    attached_file_name: Optional[str] = None
    attached_file_url: Optional[str] = None

class RateAuditorRequest(BaseModel):
    auditor_email: str
    auditor_name: str
    company_name: str
    rating: float # 1 to 5
    timeliness_rating: int = 5
    communication_rating: int = 5
    technical_rating: int = 5
    review_comment: Optional[str] = None

class AuditorReviewItemSchema(BaseModel):
    id: str
    company_name: str
    rating: float
    review_comment: Optional[str] = None
    created_at: str

class AuditorReviewsResponse(BaseModel):
    success: bool = True
    average_rating: float
    total_reviews: int
    rank: str
    subcategories: Dict[str, float]
    reviews: List[AuditorReviewItemSchema]
