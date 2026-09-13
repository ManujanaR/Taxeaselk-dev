"""Sri Lanka Corporate Income Tax (CIT) Engine
Compliant with the Inland Revenue Act No. 24 of 2017 (as amended).
"""
from typing import Dict, List, Any

def calculate_cit_waterfall(
    revenue: float = 25000000.0,
    cost_of_sales: float = 15200000.0,
    operating_expenses: float = 5200000.0,
    disallowables: float = 2100000.0,
    capital_allowances: float = 1500000.0,
    is_sme: bool = False
) -> Dict[str, Any]:
    gross_profit = revenue - cost_of_sales
    gross_margin_pct = round((gross_profit / revenue * 100), 2) if revenue > 0 else 0.0
    accounting_profit = gross_profit - operating_expenses

    # Tax adjustments under Inland Revenue Act No. 24 of 2017:
    # Taxable Income = Accounting Profit + Disallowables (Sec 11) - Capital Allowances (Sched 4)
    taxable_income = max(0.0, accounting_profit + disallowables - capital_allowances)

    cit_rate = 14 if is_sme else 30
    cit_liability = taxable_income * (cit_rate / 100.0)

    return {
        "revenue": revenue,
        "cost_of_sales": cost_of_sales,
        "gross_profit": gross_profit,
        "gross_margin_percent": gross_margin_pct,
        "operating_expenses": operating_expenses,
        "accounting_profit": accounting_profit,
        "disallowable_add_backs": disallowables,
        "tax_capital_allowances": capital_allowances,
        "taxable_income": taxable_income,
        "cit_rate_percent": cit_rate,
        "est_cit_liability": cit_liability,
        "statutory_reference": "Inland Revenue Act No. 24 of 2017"
    }

def generate_default_financial_schedules(company_name: str = "ABC (Pvt) Ltd") -> Dict[str, List[Dict[str, Any]]]:
    """Generates structured financial line items for the 5 interactive schedules:
    1. Income Statement
    2. Balance Sheet
    3. Trial Balance
    4. General Ledger
    5. Fixed Assets
    """
    return {
        "Income Statement": [
            {"id": "is_1", "name": "Gross Revenue from IT Services & Export", "amount": 25000000.0, "source": "Sales Ledger", "category": "Revenue", "taxTreatment": "Assessable Income", "aiConfidence": 99, "isSubtotal": False},
            {"id": "is_2", "name": "Direct Software Engineering Costs", "amount": -15200000.0, "source": "Cost Ledger", "category": "Cost of Sales", "taxTreatment": "Allowable Deduction", "aiConfidence": 98, "isSubtotal": False},
            {"id": "is_3", "name": "Gross Profit", "amount": 9800000.0, "source": "Computed", "category": "Gross Profit", "taxTreatment": "Subtotal", "aiConfidence": 100, "isSubtotal": True},
            {"id": "is_4", "name": "Staff Salaries & EPF/ETF (12% / 3%)", "amount": -3200000.0, "source": "Payroll Schedule", "category": "Operating", "taxTreatment": "Allowable under Sec 10", "aiConfidence": 97, "isSubtotal": False},
            {"id": "is_5", "name": "Office Rent & Colombo Facility Leases", "amount": -1100000.0, "source": "Lease Agreements", "category": "Operating", "taxTreatment": "Allowable under Sec 10", "aiConfidence": 96, "isSubtotal": False},
            {"id": "is_6", "name": "Entertainment & Hospitality Expenses", "amount": -450000.0, "source": "Vouchers", "category": "Operating", "taxTreatment": "Disallowed under Sec 11", "aiConfidence": 94, "isSubtotal": False},
            {"id": "is_7", "name": "Accounting Depreciation on Equipment", "amount": -450000.0, "source": "Fixed Asset Register", "category": "Operating", "taxTreatment": "Disallowed (Sec 11 Add-back)", "aiConfidence": 95, "isSubtotal": False},
            {"id": "is_8", "name": "Accounting Profit Before Tax (PBT)", "amount": 4600000.0, "source": "Computed", "category": "Net Profit", "taxTreatment": "Starting Tax Base", "aiConfidence": 100, "isSubtotal": True}
        ],
        "Balance Sheet": [
            {"id": "bs_1", "name": "Property, Plant & Equipment (Net)", "amount": 7500000.0, "source": "Fixed Assets Register", "category": "Non-Current Assets", "taxTreatment": "Capital Asset", "aiConfidence": 98, "isSubtotal": False},
            {"id": "bs_2", "name": "Trade & Other Receivables", "amount": 4200000.0, "source": "Debtors Ledger", "category": "Current Assets", "taxTreatment": "Subject to Bad Debt Relief", "aiConfidence": 97, "isSubtotal": False},
            {"id": "bs_3", "name": "Cash & Cash Equivalents (Commercial Bank)", "amount": 3800000.0, "source": "Bank Confirmation", "category": "Current Assets", "taxTreatment": "Verified Cash", "aiConfidence": 99, "isSubtotal": False},
            {"id": "bs_4", "name": "Total Assets", "amount": 15500000.0, "source": "Computed", "category": "Total Assets", "taxTreatment": "Subtotal", "aiConfidence": 100, "isSubtotal": True},
            {"id": "bs_5", "name": "Stated Share Capital", "amount": 5000000.0, "source": "Share Register", "category": "Equity", "taxTreatment": "Equity Base", "aiConfidence": 100, "isSubtotal": False},
            {"id": "bs_6", "name": "Retained Earnings", "amount": 7200000.0, "source": "Prior Year Audits", "category": "Equity", "taxTreatment": "Distributable Reserves", "aiConfidence": 98, "isSubtotal": False},
            {"id": "bs_7", "name": "Trade Payables & Accrued Liabilities", "amount": 3300000.0, "source": "Creditors Ledger", "category": "Current Liabilities", "taxTreatment": "Short Term", "aiConfidence": 96, "isSubtotal": False}
        ],
        "Trial Balance": [
            {"id": "tb_1", "name": "1000 - Operating Revenue", "amount": 25000000.0, "source": "Trial Balance Ledger", "category": "Credit", "taxTreatment": "Revenue", "aiConfidence": 99, "isSubtotal": False},
            {"id": "tb_2", "name": "2000 - Cost of Sales", "amount": 15200000.0, "source": "Trial Balance Ledger", "category": "Debit", "taxTreatment": "Direct Costs", "aiConfidence": 98, "isSubtotal": False},
            {"id": "tb_3", "name": "3000 - Administrative Expenses", "amount": 4750000.0, "source": "Trial Balance Ledger", "category": "Debit", "taxTreatment": "Opex", "aiConfidence": 96, "isSubtotal": False},
            {"id": "tb_4", "name": "3500 - Disallowed Expenses Pool", "amount": 450000.0, "source": "Trial Balance Ledger", "category": "Debit", "taxTreatment": "Sec 11 Adjustment", "aiConfidence": 95, "isSubtotal": False}
        ],
        "General Ledger": [
            {"id": "gl_1", "name": "GL-2026-01: Server Infrastructure & Cloud Hosting", "amount": 1850000.0, "source": "AWS & Azure Invoices", "category": "Operating Expense", "taxTreatment": "Wholly & Exclusively Deductible", "aiConfidence": 98, "isSubtotal": False},
            {"id": "gl_2", "name": "GL-2026-02: Legal & Statutory Secretarial Fees", "amount": 350000.0, "source": "Legal Firm Retainer", "category": "Professional Fees", "taxTreatment": "Allowable Expense", "aiConfidence": 97, "isSubtotal": False},
            {"id": "gl_3", "name": "GL-2026-03: Marketing & Overseas Client Acquisition", "amount": 950000.0, "source": "Marketing Receipts", "category": "Promotion", "taxTreatment": "Allowable Expense", "aiConfidence": 96, "isSubtotal": False}
        ],
        "Fixed Assets": [
            {"id": "fa_1", "name": "Server Hardware & Network Racks", "amount": 2400000.0, "source": "Fixed Asset Register", "category": "Computer Hardware (Class 2)", "taxTreatment": "20% Capital Allowance (4th Sched)", "aiConfidence": 98, "isSubtotal": False},
            {"id": "fa_2", "name": "Office Laptops & Development Workstations", "amount": 3100000.0, "source": "Asset Invoices", "category": "IT Equipment (Class 2)", "taxTreatment": "20% Capital Allowance (4th Sched)", "aiConfidence": 97, "isSubtotal": False},
            {"id": "fa_3", "name": "Office Furniture & Air Conditioning Units", "amount": 2000000.0, "source": "Fit-out Register", "category": "Office Equipment (Class 3)", "taxTreatment": "20% Capital Allowance (4th Sched)", "aiConfidence": 96, "isSubtotal": False}
        ]
    }
