import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey
from app.core.database import Base

class CompanyChecklistItem(Base):
    __tablename__ = "company_checklist_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), index=True)
    item_key = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="Statutory")
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=True)
    auditor_note = Column(Text, nullable=True)
    provided = Column(Boolean, default=False)
    assigned_auditor_name = Column(String(255), default="K.L. Perera, FCA")
    assigned_auditor_firm = Column(String(255), default="BDO Partners")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
