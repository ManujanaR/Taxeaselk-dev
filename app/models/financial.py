import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from app.core.database import Base

class FinancialSummary(Base):
    __tablename__ = "financial_summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    company_name = Column(String(255), index=True)
    tax_year = Column(String(50), default="2025/26")
    revenue = Column(Float, default=25000000.0)
    cost_of_sales = Column(Float, default=15200000.0)
    gross_profit = Column(Float, default=9800000.0)
    gross_margin_percent = Column(Float, default=39.2)
    operating_expenses = Column(Float, default=5200000.0)
    accounting_profit = Column(Float, default=4600000.0)
    disallowable_add_backs = Column(Float, default=2100000.0)
    tax_capital_allowances = Column(Float, default=1500000.0)
    taxable_income = Column(Float, default=5200000.0)
    cit_rate_percent = Column(Integer, default=30)
    est_cit_liability = Column(Float, default=1560000.0)
    auditor_status = Column(String(100), default="Under Review")
    ird_gazette_ref = Column(String(255), default="Inland Revenue Act No. 24 of 2017 (as amended 2024)")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FinancialLineItem(Base):
    __tablename__ = "financial_line_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), index=True)
    tab_name = Column(String(100), nullable=False) # "Income Statement", "Balance Sheet", "Trial Balance", "General Ledger", "Fixed Assets"
    item_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    source = Column(String(255), default="Audited Accounts / Trial Balance")
    category = Column(String(100), default="Operating")
    tax_treatment = Column(String(255), default="Standard Deductible")
    ai_confidence = Column(Integer, default=95)
    is_subtotal = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
