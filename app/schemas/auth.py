from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "business"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "business"
    full_name: Optional[str] = None
    company_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    is_active: bool = True
