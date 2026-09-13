from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FinancialLineItemSchema(BaseModel):
    id: str
    name: str
    amount: float
    source: str
    category: str
    taxTreatment: str
    aiConfidence: int
    isSubtotal: Optional[bool] = False

class FinancialsSummary(BaseModel):
    revenue: str
    costOfSales: str
    grossProfit: str
    grossMarginPercent: float
    operatingExpenses: str
    accountingProfit: str
    disallowableAddBacks: str
    taxCapitalAllowances: str
    taxableIncome: str
    citRatePercent: int
    estCitLiability: str
    auditorStatus: str
    tabs: Dict[str, List[FinancialLineItemSchema]]

class AiFinancialReportData(BaseModel):
    companyName: str
    taxYear: str
    generatedAt: str
    executiveSummary: str
    profitabilityAnalysis: str
    taxWaterfall: Dict[str, Any]
    riskScore: int
    riskLevel: str
    recommendations: List[str]
