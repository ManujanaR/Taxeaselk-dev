from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.checklist import CompanyChecklistItem
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.checklist import ChecklistPreset, ChecklistItemSchema, CompanyChecklistResponse, AuditorChecklistPublishRequest

router = APIRouter(tags=["Document Checklists"])

@router.get("/api/checklists/presets", response_model=list[ChecklistPreset])
def get_checklist_presets():
    return [
        ChecklistPreset(
            id="preset_cit_standard",
            name="Standard Statutory CIT Pack",
            description="Core statutory document set required for standard corporate income tax computation.",
            industry="General Commercial & SME",
            items=[
                ChecklistItemSchema(id="c1", key="financial_statements", name="Audited Financial Statements", category="Financial", description="Signed Balance Sheet, P&L, and Notes", required=True, auditorNote="Must bear signature of FCA/ACA auditor."),
                ChecklistItemSchema(id="c2", key="trial_balance", name="Final Trial Balance (12 Months)", category="Financial", description="Balanced 12-month TB matching accounts", required=True, auditorNote="Ensure revenue codes reconcile to RAMIS Sched 2."),
                ChecklistItemSchema(id="c3", key="general_ledger", name="Detailed General Ledger Extracts", category="Accounting", description="Operating expenses ledger breakdown", required=True, auditorNote="Highlight entertainment vouchers > Rs. 50k."),
                ChecklistItemSchema(id="c4", key="fixed_assets", name="Fixed Asset Register & Depreciation", category="Tax Schedules", description="Listing of additions, disposals, and tax depreciation", required=True, auditorNote="Reconcile 4th schedule capital allowances."),
                ChecklistItemSchema(id="c5", key="previous_cit", name="Prior Year Certified CIT Return", category="Statutory", description="Year of Assessment 2024/25 return copy", required=False, auditorNote="Optional unless loss carry-forwards are claimed.")
            ]
        ),
        ChecklistPreset(
            id="preset_boi_exporter",
            name="BOI & Export Enterprise Pack",
            description="Statutory items for zero-rated or concessionary tax treatment under BOI agreements.",
            industry="IT Exports & Manufacturing",
            items=[
                ChecklistItemSchema(id="c1", key="financial_statements", name="Audited Financial Statements", category="Financial", required=True),
                ChecklistItemSchema(id="c2", key="boi_agreement", name="BOI Agreement & Gazetted Amendments", category="Legal", description="Copy of Section 17 BOI Agreement", required=True, auditorNote="Verify active tax exemption sunset date."),
                ChecklistItemSchema(id="c3", key="export_realization", name="Bank Export Realization Certificates", category="Banking", description="Form 1/2 export proceeds banking confirmation", required=True, auditorNote="Required for 14% concessionary rate claim.")
            ]
        ),
        ChecklistPreset(
            id="preset_manufacturing",
            name="Manufacturing & Trading Pack",
            description="Tailored for entities carrying physical trading inventories and WHT deductions.",
            industry="Trading & Manufacturing",
            items=[
                ChecklistItemSchema(id="c1", key="financial_statements", name="Audited Financial Statements", category="Financial", required=True),
                ChecklistItemSchema(id="c2", key="stock_valuation", name="Physical Stock Valuation Certificate", category="Inventory", description="Inventory count signed by management", required=True, auditorNote="Check valuation method (FIFO / Weighted Avg)."),
                ChecklistItemSchema(id="c3", key="wht_sched", name="WHT / AIT Deduction Certificates", category="Tax Deductions", description="Schedule 10 bank certificates for tax credits", required=True, auditorNote="Match certificate amounts against RAMIS.")
            ]
        )
    ]

@router.get("/api/checklists/{company_name}", response_model=CompanyChecklistResponse)
def get_company_checklist(company_name: str, db: Session = Depends(get_db)):
    clean_name = company_name.replace("+", " ")
    items = db.query(CompanyChecklistItem).filter(
        (CompanyChecklistItem.company_name == company_name) | (CompanyChecklistItem.company_name == clean_name)
    ).all()
    if not items:
        presets = get_checklist_presets()
        default_items = presets[0].items
        return CompanyChecklistResponse(
            company_name=company_name,
            assignedAuditorName="K.L. Perera, FCA",
            assignedAuditorFirm="BDO Partners",
            items=default_items
        )

    res_items = [
        ChecklistItemSchema(
            id=str(it.id),
            key=it.item_key,
            name=it.name,
            category=it.category,
            description=it.description,
            required=it.required,
            auditorNote=it.auditor_note,
            provided=it.provided
        ) for it in items
    ]

    first_it = items[0]
    return CompanyChecklistResponse(
        company_name=company_name,
        assignedAuditorName=first_it.assigned_auditor_name,
        assignedAuditorFirm=first_it.assigned_auditor_firm,
        items=res_items
    )

@router.post("/api/auditor/checklists")
def publish_auditor_checklist(payload: AuditorChecklistPublishRequest, db: Session = Depends(get_db)):
    db.query(CompanyChecklistItem).filter(CompanyChecklistItem.company_name == payload.company_name).delete()

    for it in payload.items:
        db.add(CompanyChecklistItem(
            company_name=payload.company_name,
            item_key=it.key or it.id,
            name=it.name,
            category=it.category,
            description=it.description,
            required=it.required,
            auditor_note=it.auditorNote,
            provided=it.provided or False,
            assigned_auditor_name=payload.auditor_name or "K.L. Perera, FCA",
            assigned_auditor_firm=payload.auditor_firm or "BDO Partners"
        ))

    db.add(Notification(
        recipient_role="business",
        company_name=payload.company_name,
        type="info",
        title="Auditor Published Updated Checklist",
        message=f"{payload.auditor_name} updated statutory document requirements for your CIT return.",
        link="/documents"
    ))
    db.add(AuditLog(
        company_name=payload.company_name,
        actor_name=payload.auditor_name or "K.L. Perera, FCA",
        actor_role="Lead Statutory Auditor",
        event_type="CHECKLIST_PUBLISHED",
        details=f"Published custom document checklist with {len(payload.items)} items.",
        action_tone="info"
    ))
    db.commit()
    return {"success": True, "message": "Checklist published successfully to company"}
