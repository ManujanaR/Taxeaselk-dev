"""Auditor issues, requests for information (RFIs), client responses and evidence attachments."""
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import current_auditor, current_company, engagement_for_auditor, get_current_user, live_engagement
from app.models import (
    Attachment, AuditorProfile, Company, Engagement, Issue, LIVE_ENGAGEMENT_STATUSES, Request, Response, User, now,
)
from app.schemas.base import CamelModel
from app.schemas.shared import AttachmentOut, IssueOut, RequestOut, ResponseOut
from app.services import files
from app.services.notify import auditor_user_id, business_user_id, log, notify

router = APIRouter(prefix="/api", tags=["issues"])


def _business_engagement(db: Session, co: Company) -> Engagement:
    eng = live_engagement(db, co.id)
    if not eng or eng.status == "invited":
        raise HTTPException(409, "No active auditor engagement")
    return eng


# ---------- business: issues ----------

@router.post("/issues/{issue_id}/respond", response_model=IssueOut)
async def respond_to_issue(issue_id: str, response_text: str = Form(..., alias="responseText"), file: UploadFile | None = File(None),
                           co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = _business_engagement(db, co)
    issue = db.get(Issue, issue_id)
    if not issue or issue.engagement_id != eng.id:
        raise HTTPException(404, "Issue not found")
    if issue.status == "resolved":
        raise HTTPException(409, "Issue already resolved")
    issue.response_text = response_text.strip()
    issue.status = "pending_clarification"
    if file and file.filename:
        stored, size, ctype = await files.save_upload(file)
        db.add(Attachment(company_id=co.id, uploaded_by=co.user_id, issue_id=issue.id, original_name=file.filename,
                          stored_name=stored, size_bytes=size, content_type=ctype))
    notify(db, auditor_user_id(eng), "Client responded to an issue", f"{co.company_name} responded to: {issue.title}", "/responses")
    log(db, co.id, co.user_id, "ISSUE_RESPONDED", f"Responded to issue '{issue.title}'.")
    db.commit()
    db.refresh(issue)
    return issue


# ---------- business: requests ----------

@router.get("/requests", response_model=list[RequestOut])
def list_requests(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    return eng.requests if eng and eng.status != "invited" else []


@router.post("/requests/{request_id}/respond", response_model=ResponseOut, status_code=201)
async def respond_to_request(request_id: str, note: str = Form(...), attachments: list[UploadFile] = File([]),
                             co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = _business_engagement(db, co)
    req = db.get(Request, request_id)
    if not req or req.engagement_id != eng.id:
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
    notify(db, auditor_user_id(eng), "Client responded to RFI", f"{co.company_name} responded to {req.reference_code}: {req.title}", "/responses")
    log(db, co.id, co.user_id, "RFI_RESPONDED", f"Responded to {req.reference_code} ({req.title}).")
    db.commit()
    db.refresh(resp)
    return resp


# ---------- auditor: issues ----------

class IssueIn(CamelModel):
    title: str
    comment: str = ""
    source: str = ""
    severity: str = "warning"


@router.post("/auditor/engagements/{engagement_id}/issues", response_model=IssueOut, status_code=201)
def raise_issue(engagement_id: str, payload: IssueIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    if eng.status not in ("active", "under_review"):
        raise HTTPException(409, "Engagement is not active")
    if payload.severity not in ("critical", "warning"):
        raise HTTPException(422, "severity must be critical or warning")
    issue = Issue(engagement_id=eng.id, **payload.model_dump())
    db.add(issue)
    db.flush()
    notify(db, business_user_id(eng), f"Auditor raised a {payload.severity} issue", payload.title,
           f"/auditor-review?issue={issue.id}", payload.severity)
    log(db, eng.company_id, ap.user_id, "ISSUE_RAISED", f"Raised {payload.severity} issue '{payload.title}'.", "warning")
    db.commit()
    db.refresh(issue)
    return issue


@router.post("/auditor/issues/{issue_id}/resolve", response_model=IssueOut)
def resolve_issue(issue_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    issue = db.get(Issue, issue_id)
    if not issue or issue.engagement.auditor_id != ap.id:
        raise HTTPException(404, "Issue not found")
    issue.status, issue.resolved_at = "resolved", now()
    eng = issue.engagement
    notify(db, business_user_id(eng), "Issue resolved", f"{ap.firm_name} resolved: {issue.title}", "/auditor-review", "success")
    log(db, eng.company_id, ap.user_id, "ISSUE_RESOLVED", f"Resolved issue '{issue.title}'.", "success")
    db.commit()
    return issue


# ---------- auditor: requests ----------

class RequestIn(CamelModel):
    title: str
    description: str = ""
    category: str = "General Inquiry"
    priority: str = "MEDIUM"
    due_date: date | None = None


@router.post("/auditor/engagements/{engagement_id}/requests", response_model=RequestOut, status_code=201)
def create_request(engagement_id: str, payload: RequestIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    if eng.status not in ("active", "under_review"):
        raise HTTPException(409, "Engagement is not active")
    if payload.priority not in ("HIGH", "MEDIUM", "LOW"):
        raise HTTPException(422, "priority must be HIGH, MEDIUM or LOW")
    seq = db.query(Request).join(Engagement).filter(Engagement.auditor_id == ap.id).count() + 1
    req = Request(engagement_id=eng.id, reference_code=f"REQ-{eng.tax_year[:4]}-{seq:03d}", **payload.model_dump())
    db.add(req)
    db.flush()
    notify(db, business_user_id(eng), f"New request for information ({payload.priority})", f"{req.reference_code}: {req.title}",
           "/auditor-review", "warning")
    log(db, eng.company_id, ap.user_id, "RFI_CREATED", f"Issued {req.reference_code} ({req.title}).")
    db.commit()
    db.refresh(req)
    return req


def _auditor_request(db: Session, ap: AuditorProfile, request_id: str) -> Request:
    req = db.get(Request, request_id)
    if not req or req.engagement.auditor_id != ap.id:
        raise HTTPException(404, "Request not found")
    return req


@router.post("/auditor/requests/{request_id}/remind", status_code=204)
def remind(request_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    req = _auditor_request(db, ap, request_id)
    if req.status == "resolved":
        raise HTTPException(409, "Request already resolved")
    notify(db, business_user_id(req.engagement), f"Reminder: {req.reference_code} is outstanding",
           f"{ap.firm_name} is waiting for: {req.title}", "/auditor-review", "critical")
    log(db, req.engagement.company_id, ap.user_id, "RFI_REMINDER", f"Sent reminder for {req.reference_code}.", "warning")
    db.commit()


# ---------- auditor: responses ----------

class ResponseRow(ResponseOut):
    reference_code: str
    request_title: str
    category: str
    company_name: str
    engagement_id: str


def response_row(r: Response) -> ResponseRow:
    req = r.request
    return ResponseRow(**ResponseOut.model_validate(r).model_dump(), reference_code=req.reference_code, request_title=req.title,
                       category=req.category, company_name=req.engagement.company.company_name, engagement_id=req.engagement_id)


@router.get("/auditor/responses", response_model=list[ResponseRow])
def list_responses(status: str | None = None, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    q = db.query(Response).join(Request).join(Engagement).filter(Engagement.auditor_id == ap.id)
    if status:
        q = q.filter(Response.status == status)
    return [response_row(r) for r in q.order_by(Response.created_at.desc())]


def _auditor_response(db: Session, ap: AuditorProfile, response_id: str) -> Response:
    r = db.get(Response, response_id)
    if not r or r.request.engagement.auditor_id != ap.id:
        raise HTTPException(404, "Response not found")
    return r


@router.post("/auditor/responses/{response_id}/resolve", response_model=ResponseRow)
def resolve_response(response_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    r = _auditor_response(db, ap, response_id)
    r.status = r.request.status = "resolved"
    eng = r.request.engagement
    notify(db, business_user_id(eng), "Response accepted", f"{ap.firm_name} marked {r.request.reference_code} as resolved.",
           "/auditor-review", "success")
    log(db, eng.company_id, ap.user_id, "RFI_RESOLVED", f"Resolved {r.request.reference_code}.", "success")
    db.commit()
    return response_row(r)


class RevisionIn(CamelModel):
    note: str


@router.post("/auditor/responses/{response_id}/revision", response_model=ResponseRow)
def request_revision(response_id: str, payload: RevisionIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    r = _auditor_response(db, ap, response_id)
    r.status = r.request.status = "revision_requested"
    r.revision_note = payload.note.strip()
    eng = r.request.engagement
    notify(db, business_user_id(eng), f"Revision requested on {r.request.reference_code}", payload.note, "/auditor-review", "warning")
    log(db, eng.company_id, ap.user_id, "RFI_REVISION_REQUESTED", f"Requested revision on {r.request.reference_code}.", "warning")
    db.commit()
    return response_row(r)


# ---------- attachments ----------

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
