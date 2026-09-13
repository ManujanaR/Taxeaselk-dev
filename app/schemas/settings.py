from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TeamMemberSchema(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str

class CompanyFullSettings(BaseModel):
    company: Dict[str, Any]
    team: List[TeamMemberSchema]
    preferences: Dict[str, Any]
    notifications: Dict[str, Any]
    security: Dict[str, Any]

class AuditorFullSettings(BaseModel):
    profile: Dict[str, Any]
    team: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    notifications: Dict[str, Any]
    security: Dict[str, Any]
