import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.core.database import Base

class AuditorRequest(Base):
    __tablename__ = "auditor_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reference_code = Column(String(100), default="REQ-2026-001")
    company_name = Column(String(255), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Financial Statements")
    priority = Column(String(50), default="HIGH") # "HIGH", "MEDIUM", "LOW"
    due_date = Column(String(100), default="2026-11-20")
    status = Column(String(50), default="pending") # "pending", "responded", "resolved"
    requested_by = Column(String(255), default="K.L. Perera, FCA")
    created_at = Column(DateTime, default=datetime.utcnow)

class ClientResponse(Base):
    __tablename__ = "client_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("auditor_requests.id"), nullable=True)
    request_title = Column(String(255), nullable=True)
    reference_code = Column(String(100), nullable=True)
    company_name = Column(String(255), index=True)
    client_response_note = Column(Text, nullable=False)
    submitted_by = Column(String(255), default="Finance Manager")
    status = Column(String(50), default="unreviewed") # "unreviewed", "resolved", "revision_requested"
    revision_note = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class ResponseAttachment(Base):
    __tablename__ = "response_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String(36), ForeignKey("client_responses.id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(String(100), default="1.2 MB")
    file_type = Column(String(100), default="PDF")
    download_url = Column(String(500), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
