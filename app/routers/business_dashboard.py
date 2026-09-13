from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.document import Document
from app.models.engagement import Engagement
from app.models.financial import FinancialSummary
from app.models.issue import AuditorReviewIssue
from app.schemas.dashboard import DashboardSummary, DashboardStep, AttentionItem

router = APIRouter(prefix="/api", tags=["Business Dashboard"])

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.company_name == company_name).all()
    uploaded_count = len(docs)
    processed_count = len([d for d in docs if d.status in ("processed", "verified")])

    eng = db.query(Engagement).filter(Engagement.company_name == company_name).first()
    issues = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.company_name == company_name, AuditorReviewIssue.status != "resolved").all()

    fin = db.query(FinancialSummary).filter(FinancialSummary.company_name == company_name).first()
    acct_profit = f"Rs. {fin.accounting_profit / 1_000_000:.1f}M" if fin else "Rs. 4.6M"
    aud_status = eng.status.replace("_", " ") if eng else "Under Review"

    stage1_pct = min(100, int((uploaded_count / 5) * 100))
    stage2_pct = int((processed_count / max(1, uploaded_count)) * 100) if uploaded_count > 0 else 0
    stage3_pct = 100 if eng and eng.status in ("Under_Review", "Approved") else 50
    stage4_pct = eng.progress_percent if eng else 65
    stage5_pct = 100 if eng and eng.status == "Approved" else 0

    overall_progress = int((stage1_pct + stage2_pct + stage3_pct + stage4_pct + stage5_pct) / 5)
    if eng and eng.status == "Approved":
        overall_progress = 100

    steps = [
        DashboardStep(stepIndex=1, label="Gather Financial Data", state="completed" if stage1_pct == 100 else "in_progress", progressPercent=stage1_pct, ratioLabel=f"{uploaded_count}/5 files", sublabel="CIT return checklist documents", href="/documents"),
        DashboardStep(stepIndex=2, label="AI Data Extraction", state="completed" if stage2_pct == 100 else "in_progress", progressPercent=stage2_pct, ratioLabel=f"{processed_count}/{max(1, uploaded_count)} parsed", sublabel="Automated OCR & ledger mapping", href="/documents"),
        DashboardStep(stepIndex=3, label="Package & Handover", state="completed" if stage3_pct == 100 else "pending", progressPercent=stage3_pct, ratioLabel="100% packaged" if stage3_pct == 100 else "Pending", sublabel="Audit pack submitted to auditor", href="/auditor-review"),
        DashboardStep(stepIndex=4, label="Auditor Review", state="in_progress" if stage4_pct < 100 else "completed", progressPercent=stage4_pct, ratioLabel=f"{stage4_pct}% audited", sublabel="Assigned: K.L. Perera, FCA", href="/auditor-review"),
        DashboardStep(stepIndex=5, label="Final Sign-Off", state="completed" if stage5_pct == 100 else "pending", progressPercent=stage5_pct, ratioLabel="Signed Off" if stage5_pct == 100 else "Pending Sign-Off", sublabel="Approved return ready for RAMIS", href="/auditor-review")
    ]

    attention_items = []
    for iss in issues:
        attention_items.append(AttentionItem(
            id=str(iss.id),
            severity=iss.severity,
            title=iss.title,
            description=iss.comment,
            link="/auditor-review"
        ))

    if not attention_items:
        attention_items.append(AttentionItem(
            id="att_def",
            severity="info",
            title="All statutory documents in order",
            description="Your assigned auditor is currently inspecting fixed asset additions and tax depreciation schedules.",
            link="/auditor-review"
        ))

    return DashboardSummary(
        progressPercent=overall_progress,
        progressUpdatedAt="Just now",
        documentsUploaded=uploaded_count,
        documentsTotal=5,
        accountingProfit=acct_profit,
        auditorStatus=aud_status,
        steps=steps,
        attentionItems=attention_items
    )
