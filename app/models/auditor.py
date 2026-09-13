import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from app.core.database import Base

class AuditorProfile(Base):
    __tablename__ = "auditor_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    firm_name = Column(String(255), default="BDO Partners")
    firm_reg_no = Column(String(100), default="AF 004821")
    lead_auditor_name = Column(String(255), default="K.L. Perera, FCA")
    license_number = Column(String(100), default="CA-SL-40921")
    icasl_member_no = Column(String(100), default="FCA-9021")
    ird_practitioner_no = Column(String(100), default="IRD/PRAC/2026/089")
    phone = Column(String(100), default="+94 11 456 7890")
    email = Column(String(255), unique=True, index=True, default="kl.perera@bdo.lk")
    office_address = Column(Text, default="Level 12, World Trade Center, West Tower, Colombo 01")
    rating_score = Column(Float, default=4.9)
    rank_label = Column(String(100), default="Rank #1")
    total_reviews = Column(Integer, default=49)
    timeliness_score = Column(Float, default=4.9)
    communication_score = Column(Float, default=4.9)
    technical_rigor_score = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditorReview(Base):
    __tablename__ = "auditor_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auditor_id = Column(String(36), ForeignKey("auditor_profiles.id"), nullable=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    auditor_email = Column(String(255), index=True)
    auditor_name = Column(String(255))
    company_name = Column(String(255))
    tax_year = Column(String(50), default="2025/26")
    rating = Column(Float, nullable=False) # 1.0 to 5.0
    timeliness_rating = Column(Integer, default=5)
    communication_rating = Column(Integer, default=5)
    technical_rating = Column(Integer, default=5)
    review_comment = Column(Text, nullable=True)
    client_reviewer_name = Column(String(255), default="Finance Director")
    created_at = Column(DateTime, default=datetime.utcnow)
