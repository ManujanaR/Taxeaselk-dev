"""Five-stage audit handover pipeline, 20% each, 100% once the auditor signs off.

1 documents gathered -> 2 figures entered -> 3 pack handed over -> 4 auditor verifies documents -> 5 inquiries resolved & sign-off"""
from sqlalchemy.orm import Session, object_session

from app.models import Company, Document, Engagement, FinancialInputs

STAGES = [
    ("documents", "Document Gathering", "/documents"),
    ("financials", "Financial Data", "/financials"),
    ("handover", "Auditor Handover", "/auditor-review"),
    ("verification", "Auditor Verification", "/documents"),
    ("signoff", "Auditor Inquiries & Sign-Off", "/auditor-review"),
]


def pipeline(company: Company, eng: Engagement | None) -> dict:
    db: Session = object_session(company)
    docs = db.query(Document).filter(Document.company_id == company.id).all()
    has_inputs = db.query(FinancialInputs.id).filter(FinancialInputs.company_id == company.id).first() is not None
    approved = bool(eng and eng.status == "approved")
    handed_over = bool(eng and eng.status in ("under_review", "approved"))

    items = [c for c in eng.checklist_items if c.required] if eng else []
    if items:
        provided = sum(any(d.checklist_item_id == c.id for d in docs) for c in items)
        s1, r1 = int(provided / len(items) * 100), f"{provided} / {len(items)} Gathered"
    else:
        s1, r1 = min(100, int(len(docs) / 5 * 100)), f"{len(docs)} / 5 Uploaded"

    s2, r2 = (100, "Figures Entered") if has_inputs else (0, "Awaiting Figures")

    s3, r3 = (100, "Pack Dispatched") if handed_over else (0, "Not Submitted")

    sent = [d for d in docs if d.submitted_at]
    verified = sum(d.status == "verified" for d in sent)
    s4, r4 = (int(verified / len(sent) * 100), f"{verified} / {len(sent)} Verified") if sent else (0, "Pack Not Sent" if docs else "No Documents")

    if approved:
        s5, r5 = 100, "Audit Signed Off"
    elif eng and eng.status == "under_review":
        total = len(eng.requests)
        done = sum(r.status == "resolved" for r in eng.requests)
        s5 = int(done / total * 90) if total else 90  # 90 until the auditor signs off
        r5 = f"{total - done} Open Request(s)" if total - done else "Awaiting Sign-Off"
    else:
        s5, r5 = 0, "Not Started"

    values = [s1, s2, s3, s4, s5]
    ratios = [r1, r2, r3, r4, r5]
    overall = 100 if approved else int(sum(values) / 5)
    return {
        "overall_percent": overall,
        "stages": [
            {"key": k, "label": label, "progress_percent": v, "ratio_label": r, "href": href,
             "state": "done" if v == 100 else "in_progress" if v > 0 else "pending"}
            for (k, label, href), v, r in zip(STAGES, values, ratios)
        ],
    }
