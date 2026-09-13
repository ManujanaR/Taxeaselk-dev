from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.request_response import AuditorRequest, ClientResponse, ResponseAttachment
from app.models.notification import Notification
from app.schemas.request_response import (
    AuditorRequestCreate, AuditorRequestSchema, ClientResponseSchema,
    AuditorResponsesSummary, RevisionRequestNote, AttachedFileSchema
)

router = APIRouter(prefix="/api/auditor", tags=["Auditor RFIs & Client Responses"])

@router.get("/requests", response_model=list[AuditorRequestSchema])
def get_auditor_requests(company_name: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(AuditorRequest)
    if company_name:
        query = query.filter(AuditorRequest.company_name == company_name)
    requests = query.all()

    return [
        AuditorRequestSchema(
            id=str(r.id),
            reference_code=r.reference_code,
            company_name=r.company_name,
            title=r.title,
            description=r.description,
            category=r.category,
            priority=r.priority,
            due_date=r.due_date,
            status=r.status,
            requested_by=r.requested_by
        ) for r in requests
    ]

@router.post("/requests")
def create_auditor_request(payload: AuditorRequestCreate, db: Session = Depends(get_db)):
    req_count = db.query(AuditorRequest).count() + 1
    ref_code = f"REQ-2026-{req_count:03d}"

    new_req = AuditorRequest(
        reference_code=ref_code,
        company_name=payload.company_name,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        due_date=payload.due_date,
        status="pending",
        requested_by="K.L. Perera, FCA"
    )
    db.add(new_req)
    db.add(Notification(
        recipient_role="business",
        company_name=payload.company_name,
        type="warning",
        title=f"New RFI Issued: {payload.title}",
        message=f"Your auditor requested: {payload.title}. Due date: {payload.due_date}.",
        link="/auditor-review"
    ))
    db.commit()
    db.refresh(new_req)
    return {"success": True, "id": new_req.id, "reference_code": ref_code}

@router.post("/requests/{req_id}/remind")
def send_request_reminder(req_id: str, db: Session = Depends(get_db)):
    req = db.query(AuditorRequest).filter(AuditorRequest.id == req_id).first()
    if req:
        db.add(Notification(
            recipient_role="business",
            company_name=req.company_name,
            type="critical",
            title=f"URGENT: Reminder for RFI {req.reference_code}",
            message=f"Audit deadline approaching. Please upload: {req.title}.",
            link="/auditor-review"
        ))
        db.commit()
    return {"success": True, "message": "High-priority reminder sent to client"}

@router.get("/responses", response_model=AuditorResponsesSummary)
def get_client_responses(status: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(ClientResponse)
    if status and status != "all":
        query = query.filter(ClientResponse.status == status)
    responses = query.all()

    items = []
    for resp in responses:
        attachments = db.query(ResponseAttachment).filter(ResponseAttachment.response_id == resp.id).all()
        att_schemas = [
            AttachedFileSchema(
                name=a.file_name,
                size=a.file_size,
                type=a.file_type,
                download_url=a.download_url
            ) for a in attachments
        ]
        items.append(ClientResponseSchema(
            id=str(resp.id),
            requestId=str(resp.request_id) if resp.request_id else 'req_1' or "req_1",
            requestTitle=resp.request_title or "Commercial Bank Confirmation",
            reference_code=resp.reference_code or "REQ-2026-004",
            companyName=resp.company_name,
            clientResponseNote=resp.client_response_note,
            submittedBy=resp.submitted_by,
            status=resp.status,
            submittedAt=resp.submitted_at.strftime("%d %b %Y") if resp.submitted_at else "Today",
            attachedFiles=att_schemas
        ))

    unreviewed = len([i for i in items if i.status == "unreviewed"])
    return AuditorResponsesSummary(
        totalResponses=len(items),
        unreviewedCount=unreviewed,
        responses=items
    )

@router.post("/responses/{resp_id}/resolve")
def resolve_client_response(resp_id: str, db: Session = Depends(get_db)):
    resp = db.query(ClientResponse).filter(ClientResponse.id == resp_id).first()
    if resp:
        resp.status = "resolved"
        db.add(Notification(
            recipient_role="business",
            company_name=resp.company_name,
            type="success",
            title="Evidence Verified by Auditor",
            message=f"Your submission for {resp.request_title} has been accepted and resolved.",
            link="/auditor-review"
        ))
        db.commit()
    return {"success": True, "status": "resolved"}

@router.post("/responses/{resp_id}/revision")
def request_response_revision(resp_id: str, payload: RevisionRequestNote, db: Session = Depends(get_db)):
    resp = db.query(ClientResponse).filter(ClientResponse.id == resp_id).first()
    if resp:
        resp.status = "revision_requested"
        resp.revision_note = payload.note
        db.add(Notification(
            recipient_role="business",
            company_name=resp.company_name,
            type="warning",
            title="Revision Requested on Evidence",
            message=f"Auditor note: {payload.note}",
            link="/auditor-review"
        ))
        db.commit()
    return {"success": True, "status": "revision_requested"}
