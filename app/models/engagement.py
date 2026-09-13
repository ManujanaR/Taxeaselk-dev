import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.core.database import Base

class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    auditor_id = Column(String(36), ForeignKey("auditor_profiles.id"), nullable=True)
    company_name = Column(String(255), index=True)
    auditor_email = Column(String(255), index=True)
    tax_year = Column(String(50), default="2025/26")
    status = Column(String(50), default="Under_Review") # "Pending_Engagement", "Active", "Under_Review", "Approved", "Terminated"
    progress_percent = Column(Integer, default=65)
    submitted_date = Column(String(100), default="15 Oct 2026")
    expected_date = Column(String(100), default="15 Nov 2026")
    approved_count = Column(Integer, default=8)
    warnings_count = Column(Integer, default=2)
    critical_count = Column(Integer, default=1)
    pending_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
