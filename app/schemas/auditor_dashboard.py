from pydantic import BaseModel
from typing import Any, List, Dict, Optional

class PriorityReviewItem(BaseModel):
    companyName: str
    tag: str # "CRITICAL", "ATTENTION", "READY", "APPROVED"
    tagLabel: str
    detail: str
    progressPercent: int
    dueDate: str

class WorkloadBreakdown(BaseModel):
    pending: int
    inProgress: int
    waitingForCompany: int
    readyForApproval: int
    completed: int

class AuditorDashboardSummary(BaseModel):
    companiesAssigned: int
    pendingReviews: int
    criticalIssues: int
    completedThisPeriod: int
    priorityReviews: List[PriorityReviewItem]
    workload: WorkloadBreakdown

class BadgeCounts(BaseModel):
    companies: int = 0
    responses: int = 0
    requests: int = 0
    discussions: int = 0
    notifications: int = 0
