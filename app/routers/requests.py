"""Requests: the one way an auditor asks a client for something (voucher, clarification, finding).

The client answers once (note + files); the auditor resolves it or sends it back for revision.
"""
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import current_auditor, current_company, engagement_for_auditor, get_current_user, live_engagement
from app.models import Attachment, AuditorProfile, Company, Engagement, LIVE_ENGAGEMENT_STATUSES, Request, Response, User
from app.schemas.base import CamelModel
from app.schemas.shared import RequestOut, ResponseOut
from app.services import files
from app.services.notify import auditor_user_id, business_user_id, log, notify

router = APIRouter(prefix="/api", tags=["requests"])

OPEN_STATUSES = ("pending", "revision_requested")


# ---------- business ----------

@router.get("/requests", response_model=list[RequestOut])
def list_requests(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    return eng.requests if eng and eng.status != "invited" else []


@router.post("/requests/{request_id}/respond", response_model=ResponseOut, status_code=201)
async def respond_to_request(request_id: str, note: str = Form(...), attachments: list[UploadFile] = File([]),
                             co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    req = db.get(Request, request_id)
    if not eng or eng.status == "invited" or not req or req.engagement_id != eng.id:
        raise HTTPException(404, "Request not found")
    if req.status == "resolved":
        raise HTTPException(409, "Request already resolved")
    resp = req.response or Response(request_id=req.id, submitted_by=co.user_id)
    resp.note, resp.status, resp.revision_note = note.strip(), "unreviewed", ""
    db.add(resp)
    db.flush()
    for f in attachments:
        if not f.filename:
            continue
        stored, size, ctype = await files.save_upload(f)
        db.add(Attachment(company_id=co.id, uploaded_by=co.user_id, response_id=resp.id, original_name=f.filename,
                          stored_name=stored, size_bytes=size, content_type=ctype))
    req.status = "responded"
    notify(db, auditor_user_id(eng), "Client answered a request", f"{co.company_name} answered {req.reference_code}: {req.title}",
           "/requests?status=responded")
    log(db, co.id, co.user_id, "REQUEST_ANSWERED", f"Answered {req.reference_code} ({req.title}).")
    db.commit()
    db.refresh(resp)
    return resp


# ---------- auditor ----------

class RequestIn(CamelModel):
    title: str
    description: str = ""
    category: str = "General Inquiry"
    priority: str = "MEDIUM"
    due_date: date | None = None


class RequestRow(RequestOut):
    company_name: str
    company_id: str


def request_row(r: Request) -> RequestRow:
    return RequestRow(**RequestOut.model_validate(r).model_dump(), company_name=r.engagement.company.company_name, company_id=r.engagement.company_id)


@router.post("/auditor/engagements/{engagement_id}/requests", response_model=RequestRow, status_code=201)
def create_request(engagement_id: str, payload: RequestIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    if eng.status not in ("active", "under_review"):
        raise HTTPException(409, "Engagement is not active")
    if payload.priority not in ("HIGH", "MEDIUM", "LOW"):
        raise HTTPException(422, "priority must be HIGH, MEDIUM or LOW")
    if not payload.title.strip():
        raise HTTPException(422, "title is required")
    seq = db.query(Request).join(Engagement).filter(Engagement.auditor_id == ap.id).count() + 1
    req = Request(engagement_id=eng.id, reference_code=f"REQ-{eng.tax_year[:4]}-{seq:03d}", **payload.model_dump())
    db.add(req)
    db.flush()
    notify(db, business_user_id(eng), f"Auditor request ({payload.priority.title()} priority)", f"{req.reference_code}: {req.title}",
           f"/auditor-review?request={req.id}", "critical" if payload.priority == "HIGH" else "warning")
    log(db, eng.company_id, ap.user_id, "REQUEST_CREATED", f"Issued {req.reference_code} ({req.title}).")
    db.commit()
    db.refresh(req)
    return request_row(req)


@router.get("/auditor/requests", response_model=list[RequestRow])
def list_auditor_requests(ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    rows = db.query(Request).join(Engagement).filter(Engagement.auditor_id == ap.id).order_by(Request.created_at.desc()).all()
    return [request_row(r) for r in rows]


def _auditor_request(db: Session, ap: AuditorProfile, request_id: str) -> Request:
    req = db.get(Request, request_id)
    if not req or req.engagement.auditor_id != ap.id:
        raise HTTPException(404, "Request not found")
    return req


@router.post("/auditor/requests/{request_id}/remind", status_code=204)
def remind(request_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    req = _auditor_request(db, ap, request_id)
    if req.status not in OPEN_STATUSES:
        raise HTTPException(409, "Request is not waiting on the client")
    notify(db, business_user_id(req.engagement), f"Reminder: {req.reference_code} is outstanding",
           f"{ap.firm_name} is waiting for: {req.title}", f"/auditor-review?request={req.id}", "critical")
    log(db, req.engagement.company_id, ap.user_id, "REQUEST_REMINDER", f"Sent reminder for {req.reference_code}.", "warning")
    db.commit()


@router.post("/auditor/requests/{request_id}/resolve", response_model=RequestRow)
def resolve_request(request_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    req = _auditor_request(db, ap, request_id)
    if not req.response:
        raise HTTPException(409, "The client has not answered this request yet")
    req.status = req.response.status = "resolved"
    eng = req.engagement
    notify(db, business_user_id(eng), "Request resolved", f"{ap.firm_name} accepted your answer to {req.reference_code}.",
           "/auditor-review", "success")
    log(db, eng.company_id, ap.user_id, "REQUEST_RESOLVED", f"Resolved {req.reference_code}.", "success")
    db.commit()
    return request_row(req)


class RevisionIn(CamelModel):
    note: str


@router.post("/auditor/requests/{request_id}/revision", response_model=RequestRow)
def request_revision(request_id: str, payload: RevisionIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    req = _auditor_request(db, ap, request_id)
    if not req.response:
        raise HTTPException(409, "The client has not answered this request yet")
    if not payload.note.strip():
        raise HTTPException(422, "Explain what needs to change")
    req.status = req.response.status = "revision_requested"
    req.response.revision_note = payload.note.strip()
    eng = req.engagement
    notify(db, business_user_id(eng), f"Revision requested on {req.reference_code}", payload.note.strip(),
           f"/auditor-review?request={req.id}", "warning")
    log(db, eng.company_id, ap.user_id, "REQUEST_REVISION", f"Requested revision on {req.reference_code}.", "warning")
    db.commit()
    return request_row(req)


# ---------- attachments (either party of the engagement) ----------

@router.get("/attachments/{attachment_id}/file")
def download_attachment(attachment_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.get(Attachment, attachment_id)
    if not a:
        raise HTTPException(404, "Attachment not found")
    if user.role == "business":
        allowed = user.company.id == a.company_id
    else:
        allowed = db.query(Engagement.id).filter(Engagement.company_id == a.company_id, Engagement.auditor_id == user.auditor_profile.id,
                                                 Engagement.status.in_(LIVE_ENGAGEMENT_STATUSES + ("approved",))).first() is not None
    if not allowed:
        raise HTTPException(404, "Attachment not found")
    return files.serve(a.stored_name, a.original_name, a.content_type)
