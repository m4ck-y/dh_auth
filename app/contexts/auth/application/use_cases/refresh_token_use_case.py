"""Refresh token use case — validates refresh token and issues a new access token."""

import httpx
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from dh_shared.models.auth.user import AuthUser
from dh_shared.models.auth.session import Session
from dh_shared.enums import ESessionStatus
from app.shared.utils.security import verify_password, create_access_token
from app.settings.config import settings


class RefreshTokenUseCase:
    """Validates a refresh token and issues a new short-lived access token."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, refresh_token: str) -> str:
        """Validate the refresh token and return a new access_token JWT.

        Searches active sessions, verifies the token hash, fetches updated
        roles/permissions from dh_iam, and creates a fresh access token.
        Raises 401 if the token is invalid, expired, or the user is inactive.
        """
        # 1. Find the session with that refresh token (we need to be careful with hashing)
        # For simplicity in this example, we iterate or use a strategy.
        # Better: stored sessions with a partial index or UUID.
        # But let's follow the standard:

        query = select(Session).where(
            Session.status == ESessionStatus.ACTIVE,
            Session.expires_at > datetime.now(timezone.utc)
        )
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        target_session = None
        for s in sessions:
            if s.refresh_token_hash and verify_password(refresh_token, s.refresh_token_hash):
                target_session = s
                break

        if not target_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # 2. Get User Info
        query_user = select(AuthUser).where(AuthUser.id_person == target_session.id_person)
        result_user = await self.db.execute(query_user)
        user = result_user.scalar_one_or_none()

        if not user or not user.is_active:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found"
            )

        # 3. Get Roles and Permissions from dh_iam (Sync permissions)
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
                pass

        # 4. Create New Access Token
        token_data = {
            "sub": str(user.uuid),
            "email": user.username,
            "roles": roles,
            "permissions": permissions,
            "context": {
                "p_id": user.id_person
            }
        }
        new_access_token = create_access_token(data=token_data)

        # 5. Update session activity
        target_session.last_activity_at = datetime.now(timezone.utc)
        await self.db.commit()

        return new_access_token
