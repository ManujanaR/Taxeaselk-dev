from pydantic import BaseModel
from typing import List, Optional

class ChecklistItemSchema(BaseModel):
    id: str
    key: Optional[str] = None
    name: str
    category: str
    description: Optional[str] = None
    required: bool = True
    auditorNote: Optional[str] = None
    provided: Optional[bool] = False

class ChecklistPreset(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    items: List[ChecklistItemSchema]

class CompanyChecklistResponse(BaseModel):
    company_name: str
    assignedAuditorName: str
    assignedAuditorFirm: str
    items: List[ChecklistItemSchema]

class AuditorChecklistPublishRequest(BaseModel):
    company_name: str
    auditor_name: Optional[str] = "K.L. Perera, FCA"
    auditor_firm: Optional[str] = "BDO Partners"
    items: List[ChecklistItemSchema]
