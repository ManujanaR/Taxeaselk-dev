"""Statutory documents (business) + checklist and verification (auditor). Files served only to the two parties."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import current_auditor, current_company, engagement_for_auditor, get_current_user, live_engagement
from app.models import AuditorProfile, ChecklistItem, Company, Document, Engagement, User, now
from app.schemas.base import CamelModel
from app.schemas.shared import ChecklistItemIn, ChecklistItemOut, DocumentOut
from app.services import files
from app.services.notify import auditor_user_id, business_user_id, log, notify, touch

router = APIRouter(prefix="/api", tags=["documents"])

PRESETS = [
    {"id": "standard_cit", "name": "Standard Statutory CIT Pack", "items": [
        ("Audited / Draft Financial Statements", "Financial Statements", "Income statement, balance sheet, cash flow and notes for the year of assessment."),
        ("Trial Balance (12-month final)", "Trial Balance", "Closing trial balance agreeing to the financial statements."),
        ("General Ledger Extracts", "General Ledger", "Ledger detail for revenue, cost of sales and key expense accounts."),
        ("Fixed Asset Schedule", "Fixed Assets", "Additions, disposals and depreciation with Fourth Schedule allowances."),
        ("Prior Year CIT Return / Assessment", "CIT Return", "Last filed return and any IRD assessment notices."),
    ]},
    {"id": "boi_export", "name": "BOI & Exporter Pack", "items": [
        ("Audited / Draft Financial Statements", "Financial Statements", ""),
        ("Trial Balance (12-month final)", "Trial Balance", ""),
        ("General Ledger Extracts", "General Ledger", ""),
        ("Fixed Asset Schedule", "Fixed Assets", ""),
        ("Prior Year CIT Return / Assessment", "CIT Return", ""),
        ("BOI Agreement & Tax Holiday Letters", "BOI", "Board of Investment agreement and concession correspondence."),
        ("Export Realisation Certificates", "Export", "Bank export proceeds realisation certificates."),
        ("Customs CUSDEC Summary", "Customs", "Annual CUSDEC export declaration summary."),
    ]},
    {"id": "manufacturing", "name": "Manufacturing & Trading Pack", "items": [
        ("Audited / Draft Financial Statements", "Financial Statements", ""),
        ("Trial Balance (12-month final)", "Trial Balance", ""),
        ("General Ledger Extracts", "General Ledger", ""),
        ("Fixed Asset Schedule", "Fixed Assets", ""),
        ("Prior Year CIT Return / Assessment", "CIT Return", ""),
        ("Physical Stock Valuation Report", "Inventory", "Year-end stock count and valuation."),
        ("WHT / AIT Schedule 10 Certificates", "WHT", "Withholding and advance income tax credit certificates."),
    ]},
]


def company_documents(db: Session, company_id: str, submitted_only: bool = False) -> list[Document]:
    q = db.query(Document).filter(Document.company_id == company_id)
    if submitted_only:
        q = q.filter(Document.submitted_at.isnot(None))
    return q.order_by(Document.created_at.desc()).all()


def checklist_out(eng: Engagement | None, submitted_only: bool = False) -> list[ChecklistItemOut]:
    if not eng:
        return []
    out = []
    for c in eng.checklist_items:
        docs = [d for d in c.documents if d.submitted_at or not submitted_only]
        out.append(ChecklistItemOut(id=c.id, name=c.name, category=c.category, description=c.description, required=c.required,
                                    order_index=c.order_index, provided_document_id=docs[0].id if docs else None))
    return out


# ---------- business ----------

class ChecklistView(CamelModel):
    auditor_name: str | None
    auditor_firm: str | None
    items: list[ChecklistItemOut]


class DocumentsView(CamelModel):
    uploaded_count: int
    unsent_count: int
    verified_count: int
    review_required_count: int
    missing_count: int
    documents: list[DocumentOut]
    checklist: ChecklistView


@router.get("/documents", response_model=DocumentsView)
def list_documents(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    docs = company_documents(db, co.id)
    eng = live_engagement(db, co.id)
    items = checklist_out(eng if eng and eng.status != "invited" else None)
    return DocumentsView(
        uploaded_count=len(docs), unsent_count=sum(d.submitted_at is None for d in docs),
        verified_count=sum(d.status == "verified" for d in docs),
        review_required_count=sum(d.status == "review_required" for d in docs),
        missing_count=sum(1 for i in items if i.required and not i.provided_document_id),
        documents=docs,
        checklist=ChecklistView(auditor_name=eng.auditor.user.full_name if items else None,
                                auditor_firm=eng.auditor.firm_name if items else None, items=items),
    )


@router.post("/documents", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile = File(...), doc_type: str = Form("General", alias="docType"), checklist_item_id: str | None = Form(None, alias="checklistItemId"),
                          co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    item = None
    if checklist_item_id:
        item = db.get(ChecklistItem, checklist_item_id)
        if not item or not eng or item.engagement_id != eng.id:
            raise HTTPException(404, "Checklist item not found")
        doc_type = item.category or item.name
    stored, size, ctype = await files.save_upload(file)
    # Documents stay private until the handover pack is submitted; once the pack is with the auditor, new uploads go straight through.
    pack_sent = bool(eng and eng.status in ("under_review", "approved"))
    doc = Document(company_id=co.id, uploaded_by=co.user_id, checklist_item_id=item.id if item else None, name=file.filename,
                   stored_name=stored, size_bytes=size, content_type=ctype, doc_type=doc_type, submitted_at=now() if pack_sent else None)
    db.add(doc)
    log(db, co.id, co.user_id, "DOCUMENT_UPLOADED", f"Uploaded {file.filename} ({doc_type}).", "success")
    if pack_sent:
        notify(db, auditor_user_id(eng), "Client uploaded a document", f"{co.company_name} uploaded {file.filename}.",
               f"/auditor-documents?engagementId={eng.id}")
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or doc.company_id != co.id:
        raise HTTPException(404, "Document not found")
    if doc.status == "verified":
        raise HTTPException(409, "Verified documents cannot be deleted")
    files.delete_stored(doc.stored_name)
    log(db, co.id, co.user_id, "DOCUMENT_DELETED", f"Deleted {doc.name}.", "warning")
    eng = live_engagement(db, co.id)
    if doc.submitted_at and eng and eng.status != "invited":
        touch(db, auditor_user_id(eng))
    db.delete(doc)
    db.commit()


def _can_access_company(db: Session, user: User, company_id: str) -> bool:
    if user.role == "business":
        return user.company.id == company_id
    return db.query(Engagement.id).filter(Engagement.company_id == company_id,
                                          Engagement.auditor_id == user.auditor_profile.id,
                                          Engagement.status.in_(("active", "under_review", "approved"))).first() is not None


@router.get("/documents/{document_id}/file")
def download_document(document_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or not _can_access_company(db, user, doc.company_id) or (user.role == "auditor" and not doc.submitted_at):
        raise HTTPException(404, "Document not found")
    return files.serve(doc.stored_name, doc.name, doc.content_type)


# ---------- auditor ----------

class PresetOut(CamelModel):
    id: str
    name: str
    items: list[ChecklistItemIn]


@router.get("/auditor/checklist-presets", response_model=list[PresetOut])
def checklist_presets(_: AuditorProfile = Depends(current_auditor)):
    return [PresetOut(id=p["id"], name=p["name"], items=[ChecklistItemIn(name=n, category=c, description=d) for n, c, d in p["items"]])
            for p in PRESETS]


class ChecklistIn(CamelModel):
    items: list[ChecklistItemIn]


@router.put("/auditor/engagements/{engagement_id}/checklist", response_model=list[ChecklistItemOut])
def publish_checklist(engagement_id: str, payload: ChecklistIn, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    eng = engagement_for_auditor(engagement_id, ap, db)
    if eng.status not in ("active", "under_review"):
        raise HTTPException(409, "Accept the engagement before publishing a checklist")
    existing = {c.name: c for c in eng.checklist_items}
    keep = set()
    for idx, item in enumerate(payload.items):
        c = existing.get(item.name) or ChecklistItem(engagement_id=eng.id, name=item.name)
        c.category, c.description, c.required, c.order_index = item.category, item.description, item.required, idx
        db.add(c)
        keep.add(item.name)
    for name, c in existing.items():
        if name not in keep:
            db.delete(c)  # linked documents keep their file; checklist_item_id becomes NULL
    notify(db, business_user_id(eng), "Document checklist published",
           f"{ap.firm_name} requires {len(payload.items)} document(s) for {eng.tax_year}.", "/documents")
    log(db, eng.company_id, ap.user_id, "CHECKLIST_PUBLISHED", f"Published a {len(payload.items)}-item document checklist.")
    db.commit()
    db.refresh(eng)
    return checklist_out(eng)


def _auditor_document(db: Session, ap: AuditorProfile, document_id: str) -> tuple[Document, Engagement]:
    doc = db.get(Document, document_id)
    eng = live_engagement(db, doc.company_id) if doc else None
    if not doc or not doc.submitted_at or not eng or eng.auditor_id != ap.id or eng.status == "invited":
        raise HTTPException(404, "Document not found")
    return doc, eng


@router.post("/auditor/documents/{document_id}/verify", response_model=DocumentOut)
def verify_document(document_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    doc, eng = _auditor_document(db, ap, document_id)
    doc.status, doc.verified_by, doc.verified_at = "verified", ap.user_id, now()
    notify(db, business_user_id(eng), "Document verified", f"{ap.firm_name} verified {doc.name}.", "/documents", "success")
    log(db, doc.company_id, ap.user_id, "DOCUMENT_VERIFIED", f"Verified {doc.name}.", "success")
    db.commit()
    return doc


@router.post("/auditor/documents/{document_id}/flag", response_model=DocumentOut)
def flag_document(document_id: str, ap: AuditorProfile = Depends(current_auditor), db: Session = Depends(get_db)):
    doc, eng = _auditor_document(db, ap, document_id)
    doc.status, doc.verified_by, doc.verified_at = "review_required", None, None
    notify(db, business_user_id(eng), "Document needs attention", f"{ap.firm_name} flagged {doc.name} for review. Please re-upload or clarify.",
           "/documents", "warning")
    log(db, doc.company_id, ap.user_id, "DOCUMENT_FLAGGED", f"Flagged {doc.name} for review.", "warning")
    db.commit()
    return doc
