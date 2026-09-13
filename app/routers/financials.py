"""CIT inputs, computed waterfall, Gemini extraction, business dashboard and handover."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import current_company, live_engagement
from app.models import Company, Document, FinancialInputs, now
from app.schemas.base import CamelModel
from app.services import extract, pipeline
from app.services.notify import auditor_user_id, log, notify, touch
from app.services.tax_engine import compute

router = APIRouter(prefix="/api", tags=["financials"])


class InputsIn(CamelModel):
    revenue: float = 0
    cost_of_sales: float = 0
    operating_expenses: float = 0
    accounting_depreciation: float = 0
    entertainment_expenses: float = 0
    tax_depreciation_allowances: float = 0
    source_document_id: str | None = None


class InputsOut(InputsIn):
    tax_year: str
    updated_at: str


class Computed(CamelModel):
    gross_profit: float
    gross_margin_percent: float
    accounting_profit: float
    disallowables: float
    allowances: float
    taxable_income: float
    cit_rate_percent: float
    cit_liability: float


class FinancialsView(CamelModel):
    inputs: InputsOut | None
    computed: Computed | None
    rate_category: str


def _view(co: Company, fi: FinancialInputs | None) -> FinancialsView:
    if not fi:
        return FinancialsView(inputs=None, computed=None, rate_category=co.cit_tax_rate_category)
    w = compute(fi.revenue, fi.cost_of_sales, fi.operating_expenses, fi.accounting_depreciation,
                fi.entertainment_expenses, fi.tax_depreciation_allowances, co.cit_tax_rate_category)
    inputs = InputsOut(**{k: getattr(fi, k) for k in InputsIn.model_fields}, tax_year=fi.tax_year, updated_at=fi.updated_at.isoformat())
    return FinancialsView(inputs=inputs, computed=Computed(**w.__dict__), rate_category=co.cit_tax_rate_category)


def _inputs(db: Session, co: Company) -> FinancialInputs | None:
    return db.query(FinancialInputs).filter(FinancialInputs.company_id == co.id).first()


@router.get("/financials", response_model=FinancialsView)
def get_financials(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    return _view(co, _inputs(db, co))


@router.put("/financials", response_model=FinancialsView)
def put_financials(payload: InputsIn, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    if any(v < 0 for k, v in payload.model_dump().items() if k != "source_document_id"):
        raise HTTPException(422, "Figures cannot be negative")
    if payload.source_document_id:
        doc = db.get(Document, payload.source_document_id)
        if not doc or doc.company_id != co.id:
            raise HTTPException(404, "Source document not found")
    fi = _inputs(db, co) or FinancialInputs(company_id=co.id)
    for k, v in payload.model_dump().items():
        setattr(fi, k, v)
    fi.tax_year = co.financial_year
    db.add(fi)
    log(db, co.id, co.user_id, "FINANCIALS_UPDATED", "CIT computation inputs updated.")
    eng = live_engagement(db, co.id)
    if eng and eng.status != "invited":
        touch(db, auditor_user_id(eng))
    db.commit()
    db.refresh(fi)
    return _view(co, fi)


class ExtractIn(CamelModel):
    document_id: str


class ExtractOut(CamelModel):
    inputs: dict[str, float | None]
    confidence: dict[str, float]
    notes: str


@router.post("/financials/extract", response_model=ExtractOut)
def extract_financials(payload: ExtractIn, co: Company = Depends(current_company), db: Session = Depends(get_db)):
    doc = db.get(Document, payload.document_id)
    if not doc or doc.company_id != co.id:
        raise HTTPException(404, "Document not found")
    result = extract.extract_cit_inputs(doc)
    log(db, co.id, co.user_id, "FINANCIALS_EXTRACTED", f"Extracted figures from {doc.name} with Gemini.")
    db.commit()
    return ExtractOut(**result)


# ---------- dashboard ----------

class Step(CamelModel):
    key: str
    label: str
    state: str
    progress_percent: int
    ratio_label: str
    href: str


class AttentionItem(CamelModel):
    id: str
    severity: str
    title: str
    description: str
    link: str


class DashboardView(CamelModel):
    progress_percent: int
    steps: list[Step]
    documents_uploaded: int
    documents_required: int
    accounting_profit: float | None
    taxable_income: float | None
    cit_liability: float | None
    auditor_status: str  # none|invited|active|under_review|approved
    auditor_name: str | None
    auditor_firm: str | None
    attention_items: list[AttentionItem]


@router.get("/dashboard", response_model=DashboardView)
def dashboard(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    if not eng:
        from app.routers.business import current_or_last_engagement
        eng = current_or_last_engagement(db, co.id)
    p = pipeline.pipeline(co, eng)
    fin = _view(co, _inputs(db, co)).computed
    docs = db.query(Document).filter(Document.company_id == co.id).all()
    required = [c for c in eng.checklist_items if c.required] if eng else []
    items: list[AttentionItem] = []
    if eng:
        for r in eng.requests:
            if r.status in ("pending", "revision_requested"):
                items.append(AttentionItem(id=r.id, severity="critical" if r.priority == "HIGH" else "warning",
                                           title=f"{r.reference_code}: {r.title}",
                                           description=f"Revision requested: {r.response.revision_note}" if r.status == "revision_requested" and r.response else r.description,
                                           link=f"/auditor-review?request={r.id}"))
    for d in docs:
        if d.status == "review_required":
            items.append(AttentionItem(id=d.id, severity="warning", title=f"Document flagged: {d.name}",
                                       description="Your auditor asked you to re-check this document.", link="/documents"))
    return DashboardView(
        progress_percent=p["overall_percent"], steps=[Step(**s) for s in p["stages"]],
        documents_uploaded=len(docs), documents_required=len(required) or 5,
        accounting_profit=fin.accounting_profit if fin else None, taxable_income=fin.taxable_income if fin else None,
        cit_liability=fin.cit_liability if fin else None,
        auditor_status=eng.status if eng else "none",
        auditor_name=eng.auditor.user.full_name if eng else None, auditor_firm=eng.auditor.firm_name if eng else None,
        attention_items=items,
    )


@router.post("/handover", status_code=204)
def handover(co: Company = Depends(current_company), db: Session = Depends(get_db)):
    eng = live_engagement(db, co.id)
    if not eng or eng.status != "active":
        raise HTTPException(409, "You need an accepted auditor engagement before submitting the handover pack")
    if not _inputs(db, co):
        raise HTTPException(409, "Enter your financial figures before submitting")
    eng.status, eng.submitted_at = "under_review", now()
    sent = db.query(Document).filter(Document.company_id == co.id, Document.submitted_at.is_(None)).update(
        {"submitted_at": now()}, synchronize_session=False)
    notify(db, auditor_user_id(eng), "Handover pack submitted", f"{co.company_name} submitted their audit pack for {eng.tax_year} ({sent} document(s)).",
           f"/companies/{eng.id}?tab=documents", "success")
    log(db, co.id, co.user_id, "HANDOVER_SUBMITTED", "Audit handover pack submitted to auditor.", "success")
    db.commit()
