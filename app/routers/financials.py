from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.financial import FinancialSummary, FinancialLineItem
from app.models.engagement import Engagement
from app.schemas.financial import FinancialsSummary, FinancialLineItemSchema, AiFinancialReportData
from app.services.tax_engine import calculate_cit_waterfall, generate_default_financial_schedules

router = APIRouter(prefix="/api/financials", tags=["Financials & Tax Engine"])

@router.get("", response_model=FinancialsSummary)
def get_financials_summary(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    fin = db.query(FinancialSummary).filter(FinancialSummary.company_name == company_name).first()
    if not fin:
        waterfall = calculate_cit_waterfall()
        fin = FinancialSummary(
            company_name=company_name,
            revenue=waterfall["revenue"],
            cost_of_sales=waterfall["cost_of_sales"],
            gross_profit=waterfall["gross_profit"],
            gross_margin_percent=waterfall["gross_margin_percent"],
            operating_expenses=waterfall["operating_expenses"],
            accounting_profit=waterfall["accounting_profit"],
            disallowable_add_backs=waterfall["disallowable_add_backs"],
            tax_capital_allowances=waterfall["tax_capital_allowances"],
            taxable_income=waterfall["taxable_income"],
            cit_rate_percent=waterfall["cit_rate_percent"],
            est_cit_liability=waterfall["est_cit_liability"],
            auditor_status="Under Review"
        )
        db.add(fin)
        db.commit()
        db.refresh(fin)

    items_all = db.query(FinancialLineItem).filter(FinancialLineItem.company_name == company_name).all()

    tabs_dict = {
        "Income Statement": [],
        "Balance Sheet": [],
        "Trial Balance": [],
        "General Ledger": [],
        "Fixed Assets": []
    }

    if not items_all:
        defaults = generate_default_financial_schedules(company_name)
        for tab_name, it_list in defaults.items():
            for it in it_list:
                db_item = FinancialLineItem(
                    company_name=company_name,
                    tab_name=tab_name,
                    item_name=it["name"],
                    amount=it["amount"],
                    source=it["source"],
                    category=it["category"],
                    tax_treatment=it["taxTreatment"],
                    ai_confidence=it["aiConfidence"],
                    is_subtotal=it.get("isSubtotal", False)
                )
                db.add(db_item)
                tabs_dict[tab_name].append(FinancialLineItemSchema(
                    id=it["id"],
                    name=it["name"],
                    amount=it["amount"],
                    source=it["source"],
                    category=it["category"],
                    taxTreatment=it["taxTreatment"],
                    aiConfidence=it["aiConfidence"],
                    isSubtotal=it.get("isSubtotal", False)
                ))
        db.commit()
    else:
        for it in items_all:
            if it.tab_name in tabs_dict:
                tabs_dict[it.tab_name].append(FinancialLineItemSchema(
                    id=str(it.id),
                    name=it.item_name,
                    amount=it.amount,
                    source=it.source,
                    category=it.category,
                    taxTreatment=it.tax_treatment,
                    aiConfidence=it.ai_confidence,
                    isSubtotal=it.is_subtotal
                ))

    return FinancialsSummary(
        revenue=f"Rs. {fin.revenue / 1_000_000:.1f}M",
        costOfSales=f"Rs. {fin.cost_of_sales / 1_000_000:.1f}M",
        grossProfit=f"Rs. {fin.gross_profit / 1_000_000:.1f}M",
        grossMarginPercent=fin.gross_margin_percent,
        operatingExpenses=f"Rs. {fin.operating_expenses / 1_000_000:.1f}M",
        accountingProfit=f"Rs. {fin.accounting_profit / 1_000_000:.1f}M",
        disallowableAddBacks=f"Rs. {fin.disallowable_add_backs / 1_000_000:.1f}M",
        taxCapitalAllowances=f"Rs. {fin.tax_capital_allowances / 1_000_000:.1f}M",
        taxableIncome=f"Rs. {fin.taxable_income / 1_000_000:.1f}M",
        citRatePercent=fin.cit_rate_percent,
        estCitLiability=f"Rs. {fin.est_cit_liability / 1_000_000:.2f}M",
        auditorStatus=fin.auditor_status,
        tabs=tabs_dict
    )

@router.post("/generate-report", response_model=AiFinancialReportData)
def generate_ai_financial_report(payload: dict = Body(default={})):
    company_name = payload.get("company_name", "ABC (Pvt) Ltd")
    return AiFinancialReportData(
        companyName=company_name,
        taxYear="2025/26",
        generatedAt="Today",
        executiveSummary="ABC (Pvt) Ltd demonstrates solid commercial profitability with Rs. 25.0M gross turnover and 39.2% gross margin. Accounting PBT stands at Rs. 4.6M, which reconciles to Rs. 5.2M taxable income following statutory adjustments under the Inland Revenue Act No. 24 of 2017.",
        profitabilityAnalysis="Direct engineering costs account for 60.8% of top-line revenue. Administrative costs and Colombo lease expenses remain within standard industry benchmarks.",
        taxWaterfall={
            "accountingProfit": "Rs. 4.6M",
            "disallowables": "Rs. 2.1M (Sec 11: Entertainment, Depr add-back)",
            "capitalAllowances": "Rs. 1.5M (4th Sched: 20% IT hardware/software)",
            "taxableIncome": "Rs. 5.2M",
            "standardRate": "30%",
            "finalEstimatedLiability": "Rs. 1.56M"
        },
        riskScore=12,
        riskLevel="Low Risk",
        recommendations=[
            "Ensure formal tax invoices are retained for all software licenses exceeding Rs. 100,000.",
            "Maintain separate ledger accounts for staff canteen subsidies vs client entertainment to substantiate Section 10 deductibility.",
            "Verify all export remittance realizations to support VAT zero-rating."
        ]
    )

@router.post("/submit-to-auditor")
def submit_to_auditor(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    company_name = payload.get("company_name", "ABC (Pvt) Ltd")
    eng = db.query(Engagement).filter(Engagement.company_name == company_name).first()
    if eng:
        eng.status = "Under_Review"
        eng.progress_percent = max(eng.progress_percent, 50)
        db.commit()
    return {"success": True, "message": "Audit pack submitted to appointed auditor"}
