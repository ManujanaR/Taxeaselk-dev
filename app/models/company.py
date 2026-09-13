import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    company_name = Column(String(255), unique=True, index=True, nullable=False)
    trading_name = Column(String(255), nullable=True)
    registration_number = Column(String(100), default="PV 00294812")
    tin_number = Column(String(100), default="192847291-0000")
    vat_number = Column(String(100), default="293847291-7000")
    is_svat_registered = Column(Boolean, default=True)
    svat_number = Column(String(100), default="SVAT-009218")
    cit_tax_rate_category = Column(String(50), default="standard_30") # "standard_30" | "sme_concessionary_14"
    financial_year = Column(String(50), default="2025/26")
    contact_email = Column(String(255), default="finance@abc.lk")
    contact_phone = Column(String(100), default="+94 11 234 5678")
    registered_address = Column(Text, default="No. 45, Galle Road, Colombo 03, Sri Lanka")
    industry_sector = Column(String(100), default="Information Technology & Software Export")
    cit_status = Column(String(100), default="Under Review") # "Draft", "Under Review", "Ready for Auditor", "Approved", "Waiting for Company"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
