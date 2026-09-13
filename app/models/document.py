import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    company_name = Column(String(255), index=True)
    name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=True)
    doc_type = Column(String(100), nullable=False) # "Trial Balance", "Financial Statements", "General Ledger", "Fixed Assets", "Prior CIT Return"
    status = Column(String(50), default="processed") # "processing", "processed", "review_required", "verified"
    ai_confidence_percent = Column(Float, default=98.5)
    uploaded_date = Column(String(100), default="Today")
    size_label = Column(String(100), default="2.4 MB")
    uploaded_by = Column(String(255), default="Finance Team")
    created_at = Column(DateTime, default=datetime.utcnow)
