from pydantic import BaseModel
from typing import List, Optional

class CompanyDirectoryItem(BaseModel):
    id: str
    name: str
    tin: str
    financialYear: str
    citStatus: str
    criticalCount: int
    warningsCount: int
    progressPercent: int
    dueDate: str

class CompaniesSummary(BaseModel):
    companies: List[CompanyDirectoryItem]

class CompanySettingsSchema(BaseModel):
    companyName: str
    tradingName: Optional[str] = None
    registrationNumber: str
    tinNumber: str
    vatNumber: str
    isSvatRegistered: bool
    svatNumber: Optional[str] = None
    citTaxRateCategory: str
    financialYear: str
    contactEmail: str
    contactPhone: str
    registeredAddress: Optional[str] = None
    industrySector: Optional[str] = None

class CompanyCreateRequest(BaseModel):
    name: str
    tin: str
    financialYear: str = "2025/26"
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None

class ClientInvitation(BaseModel):
    id: str
    companyName: str
    senderName: str
    senderEmail: str
    financialYear: str
    estimatedTurnover: str
    status: str # "PENDING", "ACCEPTED", "DECLINED"
    sentDate: str
