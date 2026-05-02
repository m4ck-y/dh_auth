"""
Authentication endpoints for the Digital Hospital ecosystem.

Manages login, token refresh, logout, and current user profile retrieval.
All authentication is handled via HttpOnly cookies (access_token, refresh_token)
for security — no Authorization headers are used.

## Security
- Access token: short-lived JWT (default 15 min) stored in HttpOnly cookie.
- Refresh token: long-lived random token (default 30 days) stored in HttpOnly cookie.
- Tokens are never exposed to JavaScript (`httponly=True`).
"""

from fastapi import APIRouter, Depends, Response, Cookie, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.contexts.auth.application.dtos.auth_dto import LoginRequestDTO, LoginResponseDTO, MeResponseDTO
from app.contexts.auth.application.use_cases.login_use_case import LoginUseCase
from app.contexts.auth.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from app.contexts.auth.application.use_cases.get_me_use_case import GetMeUseCase
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.security import decode_access_token
from app.settings.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_db():
    """Yield an async SQLAlchemy session per request."""
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/login", response_model=LoginResponseDTO)
async def login(
    request: LoginRequestDTO, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and issue access + refresh tokens.

    Validates credentials against AuthUser table, fetches roles/permissions
    from IAM service, and sets two HttpOnly cookies:
    - `access_token`: JWT with user claims (15 min default).
    - `refresh_token`: Random token stored in Session table (30 days default).

    Returns 401 for invalid credentials and 403 for inactive users.
    """
    use_case = LoginUseCase(db)
    access_token, refresh_token, response_dto = await use_case.execute(request)

    # Set HttpOnly Cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )

    return response_dto

@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh the access token using a valid refresh token.

    Reads the `refresh_token` cookie, validates it against the Session table,
    fetches updated roles/permissions from IAM, and issues a new access_token cookie.

    Returns 401 if the refresh token is missing, expired, or invalid.
    """
    if not refresh_token:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    
    use_case = RefreshTokenUseCase(db)
    new_access_token = await use_case.execute(refresh_token)

    # Set New Access Token Cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )

    return {"message": "Token refreshed"}

@router.post("/logout")
async def logout(response: Response):
    """
    Log out the current user by deleting the auth cookies.

    Clears both `access_token` and `refresh_token` cookies from the client.
    Does not invalidate the server-side session (TTL-based expiration).
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Session closed"}

@router.get("/me", response_model=MeResponseDTO)
async def get_me(
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user's profile.

    Reads the `access_token` cookie, decodes the JWT, and fetches the full
    profile (person info, employee/company, tenants, roles, permissions).

    Returns 401 if the token is missing, expired, or invalid.
    Returns 404 if the user profile is not found in the database.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = decode_access_token(access_token)
        user_uuid = payload.get("sub")
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    use_case = GetMeUseCase(db)
    return await use_case.execute(user_uuid, roles, permissions)
