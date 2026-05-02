"""Authentication DTOs — request and response schemas for the auth context."""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

from dh_shared.enums import EVerificationStatus


class LoginRequestDTO(BaseModel):
    """Credentials for user login."""

    username: str = Field(
        ...,
        description="User identifier — email, phone number, or username.",
        examples=["user@example.com", "+525512345678", "admin_user"],
    )
    password: str = Field(
        ...,
        description="User's secret password in plain text. It is hashed server-side with bcrypt.",
        examples=["MySecurePass123!"],
    )


class UserInfoDTO(BaseModel):
    """Minimal user information returned on login."""

    email: str = Field(
        ...,
        description="Email address of the authenticated user.",
        examples=["user@example.com"],
    )


class LoginResponseDTO(BaseModel):
    """Successful login response with user summary."""

    message: str = Field(
        ...,
        description="Result message of the login operation.",
        examples=["Login successful"],
    )
    user: UserInfoDTO = Field(
        ...,
        description="Basic user information returned after authentication.",
    )


class CompanyResponseDTO(BaseModel):
    """Company linked to the user's employee record."""

    uuid: UUID = Field(
        ...,
        description="Unique identifier of the company.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="Registered business name of the company.",
        examples=["Hospital San Rafael S.A.P.I. de C.V."],
    )


class EmployeeResponseDTO(BaseModel):
    """Employee record associated with the authenticated person."""

    uuid: UUID = Field(
        ...,
        description="Unique identifier of the employee record.",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    status: str = Field(
        ...,
        description="Current employment status (ACTIVE, INACTIVE, SUSPENDED, etc.).",
        examples=["ACTIVE"],
    )
    company: Optional[CompanyResponseDTO] = Field(
        None,
        description="Company to which this employee belongs.",
    )


class TenantResponseDTO(BaseModel):
    """Tenant (organization) the user has a membership in."""

    uuid: UUID = Field(
        ...,
        description="Unique identifier of the tenant.",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    name: str = Field(
        ...,
        description="Human-readable name of the tenant.",
        examples=["Clínica Central"],
    )
    key: str = Field(
        ...,
        description="Programmatic key used to identify the tenant in API calls.",
        examples=["clinica_central"],
    )


class MeResponseDTO(BaseModel):
    """Complete profile of the authenticated user returned by GET /auth/me."""

    uuid: UUID = Field(
        ...,
        description="Person UUID — primary identifier across the system.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: Optional[str] = Field(
        None,
        description="Given name(s) of the person.",
        examples=["Juan"],
    )
    last_name: Optional[str] = Field(
        None,
        description="Family name(s) of the person.",
        examples=["Pérez"],
    )
    username: str = Field(
        ...,
        description="Username used for authentication (email in most cases).",
        examples=["juan.perez@example.com"],
    )
    verification_status: EVerificationStatus = Field(
        ...,
        description="Identity verification status of the person.",
        examples=[EVerificationStatus.APPROVED],
    )
    employee: Optional[EmployeeResponseDTO] = Field(
        None,
        description="Employee record if the person is linked to a company.",
    )
    tenants: List[TenantResponseDTO] = Field(
        default_factory=list,
        description="List of tenants (organizations) the user has access to.",
    )
    roles: List[str] = Field(
        default_factory=list,
        description="Assigned role names within the active tenant context.",
        examples=[["ADMIN", "DOCTOR"]],
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="Granular permissions granted through the assigned roles (recurso:operacion).",
        examples=[["user:create", "patient:view"]],
    )
