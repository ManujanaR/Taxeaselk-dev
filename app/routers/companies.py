from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.engagement import Engagement
from app.models.issue import AuditorReviewIssue
from app.schemas.company import (
    CompaniesSummary, CompanyDirectoryItem, CompanyCreateRequest, ClientInvitation
)

router = APIRouter(prefix="/api/auditor", tags=["Auditor Companies"])

@router.get("/companies", response_model=CompaniesSummary)
def get_auditor_companies(search: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Company)
    if search:
        query = query.filter(Company.company_name.ilike(f"%{search}%"))
    companies = query.all()

    items = []
    for c in companies:
        crit = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.company_name == c.company_name, AuditorReviewIssue.severity == "critical", AuditorReviewIssue.status != "resolved").count()
        warn = db.query(AuditorReviewIssue).filter(AuditorReviewIssue.company_name == c.company_name, AuditorReviewIssue.severity == "warning", AuditorReviewIssue.status != "resolved").count()
        eng = db.query(Engagement).filter(Engagement.company_name == c.company_name).first()

        items.append(CompanyDirectoryItem(
            id=str(c.id),
            name=c.company_name,
            tin=c.tin_number,
            financialYear=c.financial_year,
            citStatus=c.cit_status,
            criticalCount=crit,
            warningsCount=warn,
            progressPercent=eng.progress_percent if eng else 65,
            dueDate="15 Nov 2026"
        ))

    # Add mock sample companies if only 1 exists
    if len(items) < 3:
        items.extend([
            CompanyDirectoryItem(id="c_2", name="Lanka Logistics (Pvt) Ltd", tin="293847102-0000", financialYear="2025/26", citStatus="Under Review", criticalCount=0, warningsCount=1, progressPercent=80, dueDate="20 Nov 2026"),
            CompanyDirectoryItem(id="c_3", name="Ceylon Teas Exporters Ltd", tin="839201948-0000", financialYear="2025/26", citStatus="Ready for Auditor", criticalCount=0, warningsCount=0, progressPercent=100, dueDate="25 Nov 2026"),
            CompanyDirectoryItem(id="c_4", name="Colombo Tech Ventures (Pvt) Ltd", tin="492019482-0000", financialYear="2025/26", citStatus="Approved", criticalCount=0, warningsCount=0, progressPercent=100, dueDate="Completed")
        ])

    return CompaniesSummary(companies=items)

@router.post("/companies")
def add_company_to_portfolio(payload: CompanyCreateRequest, db: Session = Depends(get_db)):
    comp = Company(
        company_name=payload.name,
        tin_number=payload.tin,
        financial_year=payload.financialYear,
        contact_email=payload.contactEmail or "finance@company.lk",
        contact_phone=payload.contactPhone or "+94 11 000 0000",
        cit_status="Draft"
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"success": True, "company_id": comp.id}

@router.get("/invitations", response_model=list[ClientInvitation])
def get_client_invitations():
    return [
        ClientInvitation(
            id="inv_101",
            companyName="Apex Global Trading (Pvt) Ltd",
            senderName="Malik Fernando, CFO",
            senderEmail="malik@apextrading.lk",
            financialYear="2025/26",
            estimatedTurnover="Rs. 45.0M",
            status="PENDING",
            sentDate="Yesterday"
        ),
        ClientInvitation(
            id="inv_102",
            companyName="Southern Agro Processing Ltd",
            senderName="Ruwan Silva, Director",
            senderEmail="ruwan@southernagro.lk",
            financialYear="2025/26",
            estimatedTurnover="Rs. 18.5M",
            status="PENDING",
            sentDate="3 days ago"
        )
    ]

@router.post("/invitations/{inv_id}/accept")
def accept_client_invitation(inv_id: str, db: Session = Depends(get_db)):
    return {"success": True, "message": "Client appointment accepted successfully"}

@router.post("/invitations/{inv_id}/decline")
def decline_client_invitation(inv_id: str, db: Session = Depends(get_db)):
    return {"success": True, "message": "Client appointment declined"}
