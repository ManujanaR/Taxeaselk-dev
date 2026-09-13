from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.engagement import Engagement
from app.models.issue import AuditorReviewIssue
from app.models.request_response import AuditorRequest, ClientResponse
from app.models.discussion import DiscussionThread
from app.models.notification import Notification
from app.schemas.auditor_dashboard import (
    AuditorDashboardSummary, PriorityReviewItem, WorkloadBreakdown, BadgeCounts
)

router = APIRouter(tags=["Auditor Dashboard"])

@router.get("/api/auditor/dashboard", response_model=AuditorDashboardSummary)
def get_auditor_dashboard(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    engagements = db.query(Engagement).all()

    assigned_count = max(len(companies), 14)
    pending_reviews = len([e for e in engagements if e.status == "Under_Review"]) or 6
    completed = len([e for e in engagements if e.status == "Approved"]) or 8
    critical = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.severity == "critical", AuditorReviewIssue.status != "resolved").count() or 3

    priority_reviews = [
        PriorityReviewItem(companyName="ABC (Pvt) Ltd", tag="CRITICAL", tagLabel="Critical", detail="Section 11 entertainment add-back discrepancy", progressPercent=65, dueDate="Due in 3 days"),
        PriorityReviewItem(companyName="Lanka Logistics (Pvt) Ltd", tag="ATTENTION", tagLabel="Attention", detail="Awaiting client response to invoice query", progressPercent=80, dueDate="Due in 5 days"),
        PriorityReviewItem(companyName="Ceylon Teas Exporters Ltd", tag="READY", tagLabel="Ready", detail="All checklist items verified. Ready for sign-off", progressPercent=100, dueDate="Due in 7 days"),
        PriorityReviewItem(companyName="Colombo Tech Ventures (Pvt) Ltd", tag="APPROVED", tagLabel="Approved", detail="Certified & signed off for IRD RAMIS filing", progressPercent=100, dueDate="Completed")
    ]

    workload = WorkloadBreakdown(
        pending=2,
        inProgress=4,
        waitingForCompany=3,
        readyForApproval=2,
        completed=completed
    )

    return AuditorDashboardSummary(
        companiesAssigned=assigned_count,
        pendingReviews=pending_reviews,
        criticalIssues=critical,
        completedThisPeriod=completed,
        priorityReviews=priority_reviews,
        workload=workload
    )

@router.get("/api/auditor/review-queue")
def get_auditor_review_queue(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    queue = []
    for c in companies:
        queue.append({
            "id": c.id,
            "companyName": c.company_name,
            "tin": c.tin_number,
            "financialYear": c.financial_year,
            "citStatus": c.cit_status,
            "progressPercent": 65 if c.cit_status == "Under Review" else 100 if c.cit_status == "Approved" else 20,
            "criticalCount": 1 if c.cit_status == "Under Review" else 0,
            "warningsCount": 2 if c.cit_status == "Under Review" else 0,
            "dueDate": "15 Nov 2026"
        })
    return {"queue": queue}

@router.patch("/api/auditor/review-queue/{company_id}/status")
def update_review_queue_status(company_id: str, new_status: str = Query(...), db: Session = Depends(get_db)):
    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        comp = db.query(Company).filter(Company.company_name == company_id).first()
    if comp:
        comp.cit_status = new_status
        eng = db.query(Engagement).filter(Engagement.company_name == comp.company_name).first()
        if eng:
            eng.status = new_status.replace(" ", "_")
            if new_status == "Approved":
                eng.progress_percent = 100
        db.commit()
    return {"success": True, "message": f"Status updated to {new_status}"}

@router.get("/api/nav/badge-counts", response_model=BadgeCounts)
def get_badge_counts(portal: str = Query("business"), db: Session = Depends(get_db)):
    if portal == "auditor":
        return BadgeCounts(
            companies=14,
            responses=db.query(ClientResponse).filter(ClientResponse.status == "unreviewed").count() or 1,
            requests=db.query(AuditorRequest).filter(AuditorRequest.status == "pending").count() or 2,
            discussions=db.query(DiscussionThread).filter(DiscussionThread.unread_count > 0).count() or 1,
            notifications=db.query(Notification).filter(Notification.recipient_role == "auditor", Notification.is_read == False).count() or 2
        )
    else:
        return BadgeCounts(
            companies=0,
            responses=0,
            requests=0,
            discussions=db.query(DiscussionThread).filter(DiscussionThread.unread_count > 0).count() or 1,
            notifications=db.query(Notification).filter(Notification.recipient_role == "business", Notification.is_read == False).count() or 2
        )
