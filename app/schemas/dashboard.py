from pydantic import BaseModel
from typing import List, Optional

class DashboardStep(BaseModel):
    stepIndex: int
    label: str
    state: str # "completed", "in_progress", "pending"
    progressPercent: int
    ratioLabel: str
    sublabel: str
    href: str

class AttentionItem(BaseModel):
    id: str
    severity: str # "critical", "warning", "info"
    title: str
    description: str
    link: str

class DashboardSummary(BaseModel):
    progressPercent: int
    progressUpdatedAt: str
    documentsUploaded: int
    documentsTotal: int
    accountingProfit: str
    auditorStatus: str
    steps: List[DashboardStep]
    attentionItems: List[AttentionItem]
