import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.core.database import Base

class AuditorSettings(Base):
    __tablename__ = "auditor_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auditor_email = Column(String(255), unique=True, index=True, default="kl.perera@bdo.lk")
    profile_json = Column(Text, nullable=True)
    team_json = Column(Text, nullable=True)
    preferences_json = Column(Text, nullable=True)
    notifications_json = Column(Text, nullable=True)
    security_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
