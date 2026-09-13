"""Business-portal endpoints. Company is always the authenticated user's own."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import current_company, live_engagement
from app.models import AuditorProfile, AuditorReview, Company, Engagement, Issue, User, now
from app.schemas.auth import CompanyOut
from app.schemas.base import CamelModel
from app.schemas.shared import AuditorSummary, EngagementOut, IssueOut, ReviewIn, ReviewOut
from app.services.notify import auditor_user_id, log, notify, touch

router = APIRouter(prefix="/api", tags=["business"])


# ---------- company ----------

class CompanyIn(CamelModel):
    company_name: str
    trading_name: str = ""
    registration_number: str = ""
    tin_number: str = ""
    vat_number: str = ""
    is_svat_registered: bool = False
    svat_number: str = ""
    cit_tax_rate_category: str = "standard_30"
    financial_year: str = "2025/26"
    contact_email: str = ""
    contact_phone: str = ""
    registered_address: str = ""
    industry_sector: str = ""


@router.get("/company", response_model=CompanyOut)
def get_company(co: Company = Depends(current_company)):
    return co


@router.put("/company", response_model=CompanyOut)
def update_company(payload: CompanyIn, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    if payload.cit_tax_rate_category not in ("standard_30", "sme_14"):
        raise HTTPException(422, "Invalid CIT rate category")
    for k, v in payload.model_dump().items():
        setattr(co, k, v)
    log(db, co.id, co.user_id, "COMPANY_UPDATED", "Company profile updated.")
    eng = live_engagement(db, co.id)
    if eng:
        touch(db, auditor_user_id(eng))
    db.commit()
    db.refresh(co)
    return co


# ---------- engagement ----------

class EngagementView(CamelModel):
    engagement: EngagementOut | None
    auditor: AuditorSummary | None
    issues: list[IssueOut]
    approved_count: int
    warnings_count: int
    critical_count: int
    pending_count: int
    review: ReviewOut | None


class InviteIn(CamelModel):
    auditor_email: str
    tax_year: str = "2025/26"
    message: str = ""


def auditor_summary(db: Session, ap: AuditorProfile) -> AuditorSummary:
    avg, count = db.query(func.avg(AuditorReview.rating), func.count(AuditorReview.id)) \
        .join(Engagement, Engagement.id == AuditorReview.engagement_id) \
        .filter(Engagement.auditor_id == ap.id).one()
    return AuditorSummary(id=ap.id, name=ap.user.full_name, firm=ap.firm_name, email=ap.user.email,
                          average_rating=round(avg, 1) if avg else None, total_reviews=count)


def current_or_last_engagement(db: Session, company_id: str) -> Engagement | None:
    return live_engagement(db, company_id) or (
        db.query(Engagement).filter(Engagement.company_id == company_id, Engagement.status == "approved")
        .order_by(Engagement.approved_at.desc()).first())


@router.get("/engagement", response_model=EngagementView)
def get_engagement(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = current_or_last_engagement(db, co.id)
    if not eng:
        return EngagementView(engagement=None, auditor=None, issues=[], approved_count=0, warnings_count=0,
                              critical_count=0, pending_count=0, review=None)
    issues = eng.issues
    return EngagementView(
        engagement=eng, auditor=auditor_summary(db, eng.auditor), issues=issues,
        approved_count=sum(i.status == "resolved" for i in issues),
        warnings_count=sum(i.severity == "warning" and i.status != "resolved" for i in issues),
        critical_count=sum(i.severity == "critical" and i.status != "resolved" for i in issues),
        pending_count=sum(i.status == "pending_clarification" for i in issues),
        review=eng.review,
    )


@router.post("/engagement/invite", response_model=EngagementOut, status_code=201)
def invite_auditor(payload: InviteIn, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    if live_engagement(db, co.id):
        raise HTTPException(409, "You already have an active or pending engagement. Cancel it first.")
    auditor_user = db.query(User).filter(User.email == payload.auditor_email.lower(), User.role == "auditor").first()
    if not auditor_user:
        raise HTTPException(404, "No registered auditor with that email. Ask them to sign up first.")
    eng = Engagement(company_id=co.id, auditor_id=auditor_user.auditor_profile.id, tax_year=payload.tax_year,
                     message=payload.message, status="invited")
    db.add(eng)
    notify(db, auditor_user.id, "New engagement invitation", f"{co.company_name} invited you for tax year {payload.tax_year}.",
           "/companies?status=invited")
    log(db, co.id, co.user_id, "AUDITOR_INVITED", f"Invited {auditor_user.full_name} ({auditor_user.auditor_profile.firm_name}).")
    db.commit()
    db.refresh(eng)
    return eng


@router.post("/engagement/cancel", status_code=204)
def cancel_engagement(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    if not eng:
        raise HTTPException(404, "No active engagement")
    eng.status = "terminated"
    notify(db, auditor_user_id(eng), "Engagement cancelled", f"{co.company_name} cancelled the engagement.", "/companies", "warning")
    log(db, co.id, co.user_id, "ENGAGEMENT_CANCELLED", "Engagement with auditor cancelled.", "warning")
    db.commit()


@router.post("/engagement/review", response_model=ReviewOut, status_code=201)
def review_auditor(payload: ReviewIn, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = current_or_last_engagement(db, co.id)
    if not eng or eng.status != "approved":
        raise HTTPException(409, "You can rate the auditor once the audit is approved.")
    if eng.review:
        raise HTTPException(409, "You have already rated this engagement.")
    review = AuditorReview(engagement_id=eng.id, **payload.model_dump())
    db.add(review)
    notify(db, auditor_user_id(eng), "New client review", f"{co.company_name} rated you {payload.rating}/5.", "/auditor-dashboard", "success")
    log(db, co.id, co.user_id, "AUDITOR_RATED", f"Rated auditor {payload.rating}/5.", "success")
    db.commit()
    db.refresh(review)
    return review
