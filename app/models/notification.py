import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, DateTime
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    recipient_role = Column(String(50), default="business") # "business", "auditor"
    company_name = Column(String(255), nullable=True, index=True)
    type = Column(String(50), default="info") # "critical", "warning", "info", "success"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), default="/dashboard")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
