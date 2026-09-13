import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.core.database import Base

class AuditorReviewIssue(Base):
    __tablename__ = "auditor_review_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), index=True)
    title = Column(String(255), nullable=False)
    comment = Column(Text, nullable=False)
    source = Column(String(100), default="Trial Balance")
    status = Column(String(50), default="action_required") # "action_required", "pending_clarification", "resolved"
    severity = Column(String(50), default="warning") # "critical", "warning"
    response_text = Column(Text, nullable=True)
    attached_file_name = Column(String(255), nullable=True)
    attached_file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
