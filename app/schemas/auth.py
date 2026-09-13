from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import CamelModel


class LoginIn(CamelModel):
    email: EmailStr
    password: str


class RegisterBusinessIn(CamelModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    company_name: str = Field(min_length=1, max_length=255)
    tin_number: str = ""
    financial_year: str = "2025/26"
    industry_sector: str = ""


class RegisterAuditorIn(CamelModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    firm_name: str = Field(min_length=1, max_length=255)
    license_number: str = ""


class ChangePasswordIn(CamelModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class UserOut(CamelModel):
    id: str
    email: str
    role: str
    full_name: str
    created_at: datetime


class CompanyOut(CamelModel):
    id: str
    company_name: str
    trading_name: str
    registration_number: str
    tin_number: str
    vat_number: str
    is_svat_registered: bool
    svat_number: str
    cit_tax_rate_category: str
    financial_year: str
    contact_email: str
    contact_phone: str
    registered_address: str
    industry_sector: str


class AuditorProfileOut(CamelModel):
    id: str
    firm_name: str
    firm_reg_no: str
    license_number: str
    icasl_member_no: str
    ird_practitioner_no: str
    phone: str
    office_address: str


class SessionOut(CamelModel):
    user: UserOut
    company: CompanyOut | None = None
    auditor_profile: AuditorProfileOut | None = None
