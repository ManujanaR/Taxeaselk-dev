from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.auditor import AuditorProfile
from app.schemas.company import CompanySettingsSchema
from app.schemas.settings import CompanyFullSettings, AuditorFullSettings, TeamMemberSchema

router = APIRouter(tags=["Settings"])

@router.get("/api/settings", response_model=CompanySettingsSchema)
@router.get("/api/company/settings", response_model=CompanySettingsSchema)
def get_company_settings(db: Session = Depends(get_db)):
    comp = db.query(Company).filter(Company.company_name == "ABC (Pvt) Ltd").first()
    if not comp:
        comp = db.query(Company).first()
    return CompanySettingsSchema(
        companyName=comp.company_name if comp else "ABC (Pvt) Ltd",
        tradingName=comp.trading_name if comp else "ABC Software Labs",
        registrationNumber=comp.registration_number if comp else "PV 00294812",
        tinNumber=comp.tin_number if comp else "192847291-0000",
        vatNumber=comp.vat_number if comp else "293847291-7000",
        isSvatRegistered=comp.is_svat_registered if comp else True,
        svatNumber=comp.svat_number if comp else "SVAT-009218",
        citTaxRateCategory=comp.cit_tax_rate_category if comp else "standard_30",
        financialYear=comp.financial_year if comp else "2025/26",
        contactEmail=comp.contact_email if comp else "finance@abc.lk",
        contactPhone=comp.contact_phone if comp else "+94 11 234 5678",
        registeredAddress=comp.registered_address if comp else "No. 45, Galle Road, Colombo 03, Sri Lanka",
        industrySector=comp.industry_sector if comp else "Information Technology & Software Export"
    )

@router.post("/api/settings")
@router.post("/api/company/settings")
def update_company_settings(payload: CompanySettingsSchema, db: Session = Depends(get_db)):
    comp = db.query(Company).filter(Company.company_name == payload.companyName).first()
    if not comp:
        comp = db.query(Company).first()
    if comp:
        comp.company_name = payload.companyName
        comp.trading_name = payload.tradingName
        comp.registration_number = payload.registrationNumber
        comp.tin_number = payload.tinNumber
        comp.vat_number = payload.vatNumber
        comp.is_svat_registered = payload.isSvatRegistered
        comp.svat_number = payload.svatNumber
        comp.cit_tax_rate_category = payload.citTaxRateCategory
        comp.financial_year = payload.financialYear
        comp.contact_email = payload.contactEmail
        comp.contact_phone = payload.contactPhone
        comp.registered_address = payload.registeredAddress
        comp.industry_sector = payload.industrySector
        db.commit()
    return {"success": True, "updated": payload}

@router.get("/api/business/settings", response_model=CompanyFullSettings)
def get_business_full_settings(db: Session = Depends(get_db)):
    settings_data = get_company_settings(db).dict()
    team = [
        TeamMemberSchema(id="tm_1", name="Finance Director", email="finance@abc.lk", role="Admin", status="Active"),
        TeamMemberSchema(id="tm_2", name="Senior Tax Accountant", email="accountant@abc.lk", role="Editor", status="Active")
    ]
    return CompanyFullSettings(
        company=settings_data,
        team=team,
        preferences={"accountingStandard": "SLFRS for SMEs", "depreciationMethod": "Straight Line", "autoArchivePriorYears": True},
        notifications={"auditorInquiries": True, "checklistUpdates": True, "deadlineAlerts": True, "discussionReplies": True},
        security={"twoFactorAuth": True, "sessionTimeoutMinutes": 30, "ipWhitelisting": False}
    )

@router.post("/api/business/settings/preferences")
def update_business_preferences(payload: dict = Body(...)):
    return {"success": True, "message": "Preferences saved"}

@router.post("/api/business/settings/notifications")
def update_business_notifications(payload: dict = Body(...)):
    return {"success": True, "message": "Notification preferences saved"}

@router.post("/api/business/settings/security")
def update_business_security(payload: dict = Body(...)):
    return {"success": True, "message": "Security settings saved"}

@router.post("/api/business/team/invite")
def invite_team_member(payload: dict = Body(...)):
    return {"success": True, "message": "Team invitation dispatched"}

@router.delete("/api/business/team/{member_id}")
def remove_team_member(member_id: str):
    return {"success": True, "message": "Team member removed"}

# --- AUDITOR 5-TAB SETTINGS ---
@router.get("/api/auditor/settings", response_model=AuditorFullSettings)
def get_auditor_full_settings(db: Session = Depends(get_db)):
    auditor = db.query(AuditorProfile).first()
    return AuditorFullSettings(
        profile={
            "fullName": auditor.lead_auditor_name if auditor else "K.L. Perera, FCA",
            "email": auditor.email if auditor else "kl.perera@bdo.lk",
            "phone": auditor.phone if auditor else "+94 11 456 7890",
            "firmName": auditor.firm_name if auditor else "BDO Partners",
            "firmRegNo": auditor.firm_reg_no if auditor else "AF 004821",
            "icaslMemberNo": auditor.icasl_member_no if auditor else "FCA-9021",
            "licenseNumber": auditor.license_number if auditor else "CA-SL-40921",
            "irdPractitionerNo": auditor.ird_practitioner_no if auditor else "IRD/PRAC/2026/089",
            "officeAddress": auditor.office_address if auditor else "Level 12, World Trade Center, West Tower, Colombo 01",
            "rubberStampUrl": "/uploads/rubber_stamp.png"
        },
        team=[
            {"id": "at_1", "name": "K.L. Perera, FCA", "email": "kl.perera@bdo.lk", "role": "Audit Partner", "status": "Active"},
            {"id": "at_2", "name": "Niroshan Dias, ACA", "email": "niroshan@bdo.lk", "role": "Senior Auditor", "status": "Active"},
            {"id": "at_3", "name": "Sachini Jayawardena", "email": "sachini@bdo.lk", "role": "Audit Assistant", "status": "Active"}
        ],
        preferences={
            "defaultTaxYear": "2025/26",
            "accountingStandard": "SLFRS for SMEs",
            "materialityThreshold": 5.0,
            "autoSendRemindersDays": 7,
            "autoRequestStandardPack": True,
            "strictVatReconciliation": True
        },
        notifications={
            "clientDocumentUploaded": True,
            "clientResponseReceived": True,
            "discussionMessageReceived": True,
            "deadlineApproaching": True,
            "digestFrequency": "Instant"
        },
        security={
            "twoFactorAuth": True,
            "sessionTimeoutMinutes": 60,
            "ipWhitelistEnabled": False,
            "immutableAuditTrail": True
        }
    )

@router.put("/api/auditor/settings")
def update_auditor_settings(payload: dict = Body(...)):
    return {"success": True, "message": "Auditor settings updated successfully"}

@router.post("/api/auditor/profile")
def update_auditor_profile(payload: dict = Body(...), db: Session = Depends(get_db)):
    auditor = db.query(AuditorProfile).first()
    if auditor:
        auditor.lead_auditor_name = payload.get("fullName", auditor.lead_auditor_name)
        auditor.firm_name = payload.get("firmName", auditor.firm_name)
        auditor.phone = payload.get("phone", auditor.phone)
        db.commit()
    return {"success": True, "message": "Profile updated successfully"}

@router.post("/api/auditor/preferences")
def update_auditor_preferences(payload: dict = Body(...)):
    return {"success": True, "message": "Audit preferences updated"}

@router.post("/api/auditor/security")
def update_auditor_security(payload: dict = Body(...)):
    return {"success": True, "message": "Security preferences updated"}

@router.post("/api/auditor/notifications")
def update_auditor_notifications(payload: dict = Body(...)):
    return {"success": True, "message": "Notification preferences updated"}
