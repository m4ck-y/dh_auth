from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

class LoginRequestDTO(BaseModel):
    username: str = Field(
        ..., 
        description="The user's identifier (email, phone, or username)",
        examples=["user@example.com", "+525512345678", "admin_user"]
    )
    password: str = Field(
        ..., 
        description="The user's secret password",
        examples=["MySecurePass123!"]
    )

class UserInfoDTO(BaseModel):
    email: str = Field(..., examples=["user@example.com"])

class LoginResponseDTO(BaseModel):
    message: str = Field(..., examples=["Login successful"])
    user: UserInfoDTO

class CompanyResponseDTO(BaseModel):
    uuid: UUID
    name: str

class EmployeeResponseDTO(BaseModel):
    uuid: UUID
    status: str
    company: Optional[CompanyResponseDTO] = None

class TenantResponseDTO(BaseModel):
    uuid: UUID
    name: str
    key: str

class MeResponseDTO(BaseModel):
    uuid: UUID = Field(..., examples=["550e8400-e29b-41d4-a716-446655440000"])
    first_name: Optional[str] = Field(None, examples=["Juan"])
    last_name: Optional[str] = Field(None, examples=["Pérez"])
    username: str = Field(..., examples=["juan.perez"])
    verification_status: str = Field(..., examples=["APPROVED"])
    employee: Optional[EmployeeResponseDTO] = None
    tenants: List[TenantResponseDTO] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list, examples=[["ADMIN", "DOCTOR"]])
    permissions: List[str] = Field(default_factory=list, examples=[["user:create", "patient:view"]])
