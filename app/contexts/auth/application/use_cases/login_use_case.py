"""Login use case — validates credentials and issues access + refresh tokens."""

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timedelta, timezone
from dh_shared.models.auth.user import AuthUser
from dh_shared.models.auth.session import Session
from app.contexts.auth.application.dtos.auth_dto import LoginRequestDTO, LoginResponseDTO, UserInfoDTO
from app.shared.utils.security import verify_password, create_access_token, generate_random_token, hash_password
from app.settings.config import settings


class LoginUseCase:
    """Orchestrates user authentication: credential validation, IAM sync, token issuance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, dto: LoginRequestDTO) -> tuple[str, str, LoginResponseDTO]:
        """Validate credentials and return (access_token, refresh_token, response_dto).

        Raises 401 if credentials are invalid, 403 if the user is inactive.
        Fetches roles and permissions from dh_iam on success.
        Creates a new Session record for the refresh token.
        """
        # 1. Find user
        query = select(AuthUser).where(AuthUser.username == dto.username)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        # 2. Validate credentials
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials"
            )

        if not verify_password(dto.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        # 3. Get Roles and Permissions from dh_iam
        roles = []
        permissions = []

        if settings.SERVICE_IAM_URL:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    iam_response = await client.get(
                        f"{settings.SERVICE_IAM_URL}/v1/iam/context/{user.uuid}"
                    )
                    if iam_response.status_code == 200:
                        iam_data = iam_response.json().get("data", {})
                        roles = iam_data.get("roles", [])
                        permissions = iam_data.get("permissions", [])
            except Exception:
                # Fallback for dev or if IAM is down
                pass

        # 4. Create Token
        token_data = {
            "sub": str(user.uuid),
            "email": user.username,
            "roles": roles,
            "permissions": permissions,
            "context": {
                "p_id": user.id_person
            }
        }
        access_token = create_access_token(data=token_data)

        # 5. Create Refresh Token and Session
        refresh_token = generate_random_token()
        session = Session(
            id_person=user.id_person,
            refresh_token_hash=hash_password(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        await self.db.commit()

        # 6. Prepare Response
        response_dto = LoginResponseDTO(
            message="Login successful",
            user=UserInfoDTO(email=user.username)
        )

        return access_token, refresh_token, response_dto
