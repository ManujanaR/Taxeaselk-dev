import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), index=True)
    actor_name = Column(String(255), default="Lead Auditor")
    actor_role = Column(String(100), default="FCA / Partner")
    event_type = Column(String(100), default="CIT_REVIEW_UPDATE")
    details = Column(Text, nullable=False)
    action_tone = Column(String(50), default="info") # "success", "warning", "info"
    created_at = Column(DateTime, default=datetime.utcnow)
