from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from dh_shared.models.auth.user import AuthUser
from dh_shared.models.people.person import Person
from dh_shared.models.organizations.employee import Employee
from dh_shared.models.organizations.company import Company
from dh_shared.models.iam.membership import Membership
from dh_shared.models.iam.tenant import Tenant
from app.contexts.auth.application.dtos.auth_dto import (
    MeResponseDTO, EmployeeResponseDTO, CompanyResponseDTO, TenantResponseDTO
)

class GetMeUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_uuid: str, roles: list[str] = [], permissions: list[str] = []) -> MeResponseDTO:
        # Complex query with nested relationships across 4 schemas: auth, people, org, iam
        query = (
            select(AuthUser)
            .where(AuthUser.uuid == user_uuid)
            .options(
                selectinload(AuthUser.person).selectinload(Person.employees).selectinload(Employee.company),
                selectinload(AuthUser.person).selectinload(Person.memberships).selectinload(Membership.tenant)
            )
        )
        
        result = await self.db.execute(query)
        auth_user = result.scalar_one_or_none()
        
        if not auth_user or not auth_user.person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        person = auth_user.person
        
        # Build Employee info if exists
        employee_dto = None
        if person.employees:
            # We take the first active or latest employee for simplicity in /me
            emp = person.employees[0]
            comp_dto = None
            if emp.company:
                comp_dto = CompanyResponseDTO(
                    uuid=emp.company.uuid,
                    name=emp.company.name
                )
            employee_dto = EmployeeResponseDTO(
                uuid=emp.uuid,
                status=emp.status.value,
                company=comp_dto
            )
            
        # Build Tenants info
        tenants_list = []
        for m in person.memberships:
            if m.tenant:
                tenants_list.append(TenantResponseDTO(
                    uuid=m.tenant.uuid,
                    name=m.tenant.name,
                    key=m.tenant.key
                ))
        
        return MeResponseDTO(
            uuid=person.uuid,
            first_name=person.first_name,
            last_name=person.last_name,
            username=auth_user.username,
            verification_status=person.verification_status.value,
            employee=employee_dto,
            tenants=tenants_list,
            roles=roles,
            permissions=permissions
        )
