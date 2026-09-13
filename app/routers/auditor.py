"""Auditor-portal endpoints. Every engagement is checked to belong to the authenticated auditor."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, object_session

from app.core.database import get_db
from app.core.deps import current_auditor, engagement_for_auditor
from app.models import (
    AuditLog, AuditorProfile, AuditorReview, Engagement, Issue, LIVE_ENGAGEMENT_STATUSES, Request, now,
)
from app.schemas.auth import AuditorProfileOut, CompanyOut
from app.schemas.base import CamelModel
from app.schemas.shared import AuditLogOut, ChecklistItemOut, DocumentOut, EngagementOut, IssueOut, RequestOut
from app.services.notify import business_user_id, log, notify

router = APIRouter(prefix="/api/auditor", tags=["auditor"])


# ---------- profile ----------

class ProfileIn(CamelModel):
    full_name: str
    firm_name: str
    firm_reg_no: str = ""
    license_number: str = ""
    icasl_member_no: str = ""
    ird_practitioner_no: str = ""
    phone: str = ""
    office_address: str = ""


class ProfileOut(AuditorProfileOut):
    full_name: str
    email: str


def profile_out(ap: AuditorProfile) -> ProfileOut:
    return ProfileOut(**AuditorProfileOut.model_validate(ap).model_dump(), full_name=ap.user.full_name, email=ap.user.email)


@router.get("/profile", response_model=ProfileOut)
def get_profile(ap: AuditorProfile = Depends(current_auditor)):
    return profile_out(ap)


@router.put("/profile", response_model=ProfileOut)
def update_profile(payload: ProfileIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    data = payload.model_dump()
    ap.user.full_name = data.pop("full_name")
    for k, v in data.items():
        setattr(ap, k, v)
    db.commit()
    return profile_out(ap)


# ---------- engagements ----------

class EngagementRow(EngagementOut):
    company_name: str
    tin_number: str
    financial_year: str
    critical_count: int
    warnings_count: int
    open_requests: int
    progress_percent: int
    documents_count: int
    verified_count: int


def progress_of(eng: Engagement) -> int:
    from app.services.pipeline import pipeline  # local import: pipeline imports models
    return pipeline(eng.company, eng)["overall_percent"]


def row(eng: Engagement) -> EngagementRow:
    from app.models import Document
    open_issues = [i for i in eng.issues if i.status != "resolved"]
    docs = object_session(eng).query(Document.status).filter(Document.company_id == eng.company_id).all()
    return EngagementRow(
        **EngagementOut.model_validate(eng).model_dump(),
        company_name=eng.company.company_name, tin_number=eng.company.tin_number,
        financial_year=eng.company.financial_year,
        critical_count=sum(i.severity == "critical" for i in open_issues),
        warnings_count=sum(i.severity == "warning" for i in open_issues),
        open_requests=sum(r.status != "resolved" for r in eng.requests),
        progress_percent=progress_of(eng), documents_count=len(docs), verified_count=sum(d.status == "verified" for d in docs),
    )


@router.get("/engagements", response_model=list[EngagementRow])
def list_engagements(status: str | None = None, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    q = db.query(Engagement).filter(Engagement.auditor_id == ap.id)
    q = q.filter(Engagement.status == status) if status else q.filter(Engagement.status.in_(LIVE_ENGAGEMENT_STATUSES + ("approved",)))
    return [row(e) for e in q.order_by(Engagement.created_at.desc())]


class EngagementDetail(CamelModel):
    engagement: EngagementRow
    company: CompanyOut
    documents: list[DocumentOut]
    checklist: list[ChecklistItemOut]
    issues: list[IssueOut]
    requests: list[RequestOut]


@router.get("/engagements/{engagement_id}", response_model=EngagementDetail)
def engagement_detail(engagement_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    from app.routers.documents import company_documents, checklist_out  # avoid circular import at module load
    eng = engagement_for_auditor(engagement_id, ap, db)
    return EngagementDetail(engagement=row(eng), company=eng.company, documents=company_documents(db, eng.company_id),
                            checklist=checklist_out(eng), issues=eng.issues, requests=eng.requests)


def _transition(eng: Engagement, from_statuses: tuple, to: str):
    if eng.status not in from_statuses:
        raise HTTPException(409, f"Engagement is {eng.status}, cannot move to {to}")
    eng.status = to


@router.post("/engagements/{engagement_id}/accept", response_model=EngagementRow)
def accept(engagement_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    _transition(eng, ("invited",), "active")
    eng.accepted_at = now()
    notify(db, business_user_id(eng), "Auditor accepted your invitation",
           f"{ap.user.full_name} ({ap.firm_name}) is now your assigned auditor.", "/auditor-review", "success")
    log(db, eng.company_id, ap.user_id, "ENGAGEMENT_ACCEPTED", f"{ap.firm_name} accepted the engagement.", "success")
    db.commit()
    return row(eng)


@router.post("/engagements/{engagement_id}/decline", response_model=EngagementRow)
def decline(engagement_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    _transition(eng, ("invited",), "declined")
    notify(db, business_user_id(eng), "Auditor declined your invitation",
           f"{ap.user.full_name} ({ap.firm_name}) declined. You can invite another auditor.", "/auditor-review", "warning")
    log(db, eng.company_id, ap.user_id, "ENGAGEMENT_DECLINED", f"{ap.firm_name} declined the engagement.", "warning")
    db.commit()
    return row(eng)


@router.post("/engagements/{engagement_id}/approve", response_model=EngagementRow)
def approve(engagement_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    if any(i.status != "resolved" for i in eng.issues) or any(r.status != "resolved" for r in eng.requests):
        raise HTTPException(409, "Resolve all open issues and requests before signing off.")
    _transition(eng, ("under_review",), "approved")
    eng.approved_at = now()
    notify(db, business_user_id(eng), "Audit signed off",
           f"{ap.firm_name} approved your CIT computation for {eng.tax_year}.", "/dashboard", "success")
    log(db, eng.company_id, ap.user_id, "AUDIT_APPROVED", f"CIT return for {eng.tax_year} certified by {ap.firm_name}.", "success")
    db.commit()
    return row(eng)


# ---------- dashboard / reviews / audit log ----------

class PriorityReview(CamelModel):
    engagement_id: str
    company_name: str
    tag: str
    detail: str
    progress_percent: int
    due_date: date | None


class Workload(CamelModel):
    invited: int
    active: int
    under_review: int
    approved: int


class DashboardOut(CamelModel):
    companies_assigned: int
    pending_reviews: int
    critical_issues: int
    completed_this_period: int
    priority_reviews: list[PriorityReview]
    workload: Workload
    recent_activity: list[AuditLogOut]


def audit_log_out(entry: AuditLog) -> AuditLogOut:
    return AuditLogOut(id=entry.id, company_id=entry.company_id, company_name=entry.company.company_name,
                       actor_name=entry.actor.full_name, actor_role=entry.actor.role, event_type=entry.event_type,
                       details=entry.details, tone=entry.tone, created_at=entry.created_at)


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    engs = db.query(Engagement).filter(Engagement.auditor_id == ap.id).all()
    by = lambda s: [e for e in engs if e.status == s]
    live = [e for e in engs if e.status in ("active", "under_review")]
    priority = []
    for e in sorted(live, key=lambda e: (e.status != "under_review", e.created_at)):
        open_issues = [i for i in e.issues if i.status != "resolved"]
        open_reqs = [r for r in e.requests if r.status != "resolved"]
        if any(i.severity == "critical" for i in open_issues):
            tag, detail = "CRITICAL", f"{sum(i.severity == 'critical' for i in open_issues)} critical issue(s) open"
        elif e.status == "under_review" and not open_issues and not open_reqs:
            tag, detail = "READY", "Handover pack received, no open items — ready to sign off"
        elif open_issues or open_reqs:
            tag, detail = "ATTENTION", f"Awaiting client response on {len(open_issues) + len(open_reqs)} item(s)"
        else:
            tag, detail = "ACTIVE", "Awaiting handover pack from client"
        due = min((r.due_date for r in open_reqs if r.due_date), default=None)
        priority.append(PriorityReview(engagement_id=e.id, company_name=e.company.company_name, tag=tag, detail=detail,
                                       progress_percent=progress_of(e), due_date=due))
    company_ids = [e.company_id for e in engs]
    activity = (db.query(AuditLog).filter(AuditLog.company_id.in_(company_ids)).order_by(AuditLog.created_at.desc()).limit(10).all()
                if company_ids else [])
    return DashboardOut(
        companies_assigned=len(live), pending_reviews=len(by("under_review")),
        critical_issues=sum(1 for e in live for i in e.issues if i.severity == "critical" and i.status != "resolved"),
        completed_this_period=len(by("approved")), priority_reviews=priority[:6],
        workload=Workload(invited=len(by("invited")), active=len(by("active")), under_review=len(by("under_review")), approved=len(by("approved"))),
        recent_activity=[audit_log_out(a) for a in activity],
    )


class ReviewsOut(CamelModel):
    average_rating: float | None
    total_reviews: int
    timeliness: float | None
    communication: float | None
    technical: float | None
    completed_audits: int
    reviews: list["ReviewRow"]


class ReviewRow(CamelModel):
    id: str
    company_name: str
    rating: int
    comment: str
    created_at: date


@router.get("/reviews", response_model=ReviewsOut)
def reviews(ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    q = db.query(AuditorReview).join(Engagement).filter(Engagement.auditor_id == ap.id)
    avg = q.with_entities(func.avg(AuditorReview.rating), func.avg(AuditorReview.timeliness),
                          func.avg(AuditorReview.communication), func.avg(AuditorReview.technical)).one()
    rows = q.order_by(AuditorReview.created_at.desc()).all()
    r1 = lambda v: round(v, 1) if v is not None else None
    return ReviewsOut(
        average_rating=r1(avg[0]), total_reviews=len(rows), timeliness=r1(avg[1]), communication=r1(avg[2]), technical=r1(avg[3]),
        completed_audits=db.query(Engagement).filter(Engagement.auditor_id == ap.id, Engagement.status == "approved").count(),
        reviews=[ReviewRow(id=r.id, company_name=r.engagement.company.company_name, rating=r.rating, comment=r.comment,
                           created_at=r.created_at.date()) for r in rows],
    )


@router.get("/audit-log", response_model=list[AuditLogOut])
def audit_log(company_id: str | None = None, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    company_ids = [e.company_id for e in db.query(Engagement.company_id).filter(Engagement.auditor_id == ap.id)]
    if company_id:
        if company_id not in company_ids:
            raise HTTPException(404, "Company not found")
        company_ids = [company_id]
    if not company_ids:
        return []
    return [audit_log_out(a) for a in db.query(AuditLog).filter(AuditLog.company_id.in_(company_ids))
            .order_by(AuditLog.created_at.desc()).limit(200)]
