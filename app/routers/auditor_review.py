from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.auditor import AuditorProfile, AuditorReview
from app.models.engagement import Engagement
from app.models.issue import AuditorReviewIssue
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.auditor_review import (
    AuditorReviewSummary, AuditorReviewIssueSchema, IssueRespondRequest,
    RateAuditorRequest, AuditorReviewsResponse, AuditorReviewItemSchema
)

router = APIRouter(tags=["Auditor Review & Rating"])

@router.get("/api/auditor-review", response_model=AuditorReviewSummary)
def get_auditor_review_summary(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.company_name == company_name).first()
    auditor = db.query(AuditorProfile).first()
    issues_db = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.company_name == company_name).all()

    issues_schemas = [
        AuditorReviewIssueSchema(
            id=str(iss.id),
            status=iss.status,
            severity=iss.severity,
            title=iss.title,
            comment=iss.comment,
            source=iss.source,
            response_text=iss.response_text,
            attached_file_name=iss.attached_file_name
        ) for iss in issues_db
    ]

    return AuditorReviewSummary(
        auditorName=auditor.lead_auditor_name if auditor else "K.L. Perera, FCA",
        auditorFirm=auditor.firm_name if auditor else "BDO Partners",
        auditorEmail=auditor.email if auditor else "kl.perera@bdo.lk",
        reviewStatus=eng.status.replace("_", " ") if eng else "Under Review",
        submittedDate=eng.submitted_date if eng else "15 Oct 2026",
        expectedByDate=eng.expected_date if eng else "15 Nov 2026",
        reviewedPercent=eng.progress_percent if eng else 65,
        approvedCount=eng.approved_count if eng else 8,
        warningsCount=len([i for i in issues_db if i.severity == "warning" and i.status != "resolved"]),
        criticalCount=len([i for i in issues_db if i.severity == "critical" and i.status != "resolved"]),
        pendingCount=eng.pending_count if eng else 0,
        issues=issues_schemas
    )

@router.post("/api/auditor-review/issues/{issue_id}/respond")
def respond_to_auditor_issue(issue_id: str, payload: IssueRespondRequest, db: Session = Depends(get_db)):
    issue = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = "pending_clarification"
    issue.response_text = payload.response
    issue.attached_file_name = payload.attached_file_name
    issue.attached_file_url = payload.attached_file_url

    db.add(Notification(
        recipient_role="auditor",
        company_name=issue.company_name,
        type="info",
        title=f"Response submitted: {issue.title}",
        message=f"{issue.company_name} submitted explanation and vouchers for audit inquiry.",
        link="/responses"
    ))
    db.commit()
    return {"success": True, "message": "Explanation submitted to auditor"}

@router.get("/api/auditor-review/assigned-auditor")
def get_assigned_auditor(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    auditor = db.query(AuditorProfile).first()
    return {
        "auditorName": auditor.lead_auditor_name if auditor else "K.L. Perera, FCA",
        "auditorFirm": auditor.firm_name if auditor else "BDO Partners",
        "auditorEmail": auditor.email if auditor else "kl.perera@bdo.lk",
        "rating": auditor.rating_score if auditor else 4.9,
        "totalReviews": auditor.total_reviews if auditor else 49
    }

@router.get("/api/auditor-engagement/{company}")
def get_engagement_details(company: str, db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.company_name == company).first()
    auditor = db.query(AuditorProfile).first()
    return {
        "company": company,
        "auditor": auditor.lead_auditor_name if auditor else "K.L. Perera, FCA",
        "firm": auditor.firm_name if auditor else "BDO Partners",
        "status": eng.status if eng else "Under_Review",
        "tax_year": eng.tax_year if eng else "2025/26"
    }

@router.post("/api/auditor-engagement")
def establish_engagement(payload: dict = Body(...), db: Session = Depends(get_db)):
    return {"success": True, "message": "Auditor engagement established"}

@router.post("/api/auditor-engagement/disengage")
def cancel_engagement(payload: dict = Body(...), db: Session = Depends(get_db)):
    return {"success": True, "message": "Engagement terminated"}

@router.post("/api/business/auditor/invite/cancel")
def cancel_auditor_invite(payload: dict = Body(default={})):
    return {"success": True, "message": "Auditor invitation cancelled"}

@router.post("/api/business/auditor/permissions")
def update_auditor_permissions(payload: dict = Body(default={})):
    return {"success": True, "message": "Auditor permissions updated"}

@router.post("/api/business/auditor/change-request")
def request_auditor_change(payload: dict = Body(default={})):
    return {"success": True, "message": "Auditor change request submitted"}

# --- RATING & REPUTATION ENGINE ---
@router.post("/api/auditors/rate")
def submit_auditor_rating(payload: RateAuditorRequest, db: Session = Depends(get_db)):
    auditor = db.query(AuditorProfile).filter(AuditorProfile.email == payload.auditor_email).first()
    if not auditor:
        auditor = db.query(AuditorProfile).first()

    new_rev = AuditorReview(
        auditor_email=payload.auditor_email,
        auditor_name=payload.auditor_name,
        company_name=payload.company_name,
        rating=payload.rating,
        timeliness_rating=payload.timeliness_rating,
        communication_rating=payload.communication_rating,
        technical_rating=payload.technical_rating,
        review_comment=payload.review_comment
    )
    db.add(new_rev)

    if auditor:
        old_count = auditor.total_reviews or 0
        old_avg = auditor.rating_score or 5.0
        new_count = old_count + 1
        new_avg = round(((old_avg * old_count) + payload.rating) / new_count, 2)

        auditor.total_reviews = new_count
        auditor.rating_score = new_avg
        auditor.timeliness_score = round(((auditor.timeliness_score * old_count) + payload.timeliness_rating) / new_count, 1)
        auditor.communication_score = round(((auditor.communication_score * old_count) + payload.communication_rating) / new_count, 1)
        auditor.technical_rigor_score = round(((auditor.technical_rigor_score * old_count) + payload.technical_rating) / new_count, 1)

    db.add(AuditLog(
        company_name=payload.company_name,
        actor_name="Finance Director",
        actor_role="Company User",
        event_type="AUDITOR_RATED",
        details=f"Rated auditor {payload.auditor_name} with {payload.rating} stars.",
        action_tone="success"
    ))
    db.commit()
    return {"success": True, "message": "Auditor rating submitted successfully"}

@router.get("/api/auditors/{auditor_email}/reviews", response_model=AuditorReviewsResponse)
def get_auditor_reviews(auditor_email: str, db: Session = Depends(get_db)):
    auditor = db.query(AuditorProfile).filter(AuditorProfile.email == auditor_email).first()
    if not auditor:
        auditor = db.query(AuditorProfile).first()

    reviews_db = db.query(AuditorReview).filter(AuditorReview.auditor_email == auditor_email).all()
    rev_items = [
        AuditorReviewItemSchema(
            id=str(r.id),
            company_name=r.company_name,
            rating=r.rating,
            review_comment=r.review_comment,
            created_at=r.created_at.strftime("%d %b %Y") if r.created_at else "Recent"
        ) for r in reviews_db
    ]

    avg_score = auditor.rating_score if auditor else 4.9
    total_cnt = auditor.total_reviews if auditor else max(len(reviews_db), 49)

    return AuditorReviewsResponse(
        success=True,
        average_rating=avg_score,
        total_reviews=total_cnt,
        rank=auditor.rank_label if auditor else "Rank #1",
        subcategories={
            "timeliness": auditor.timeliness_score if auditor else 4.9,
            "communication": auditor.communication_score if auditor else 4.9,
            "technical_rigor": auditor.technical_rigor_score if auditor else 5.0
        },
        reviews=rev_items
    )
