"""Security utilities: JWT creation/validation and random token generation.

Uses PyJWT for encoding/decoding and delegates bcrypt hashing to dh_shared.
"""

import jwt
import secrets
from datetime import datetime, timedelta, timezone
from dh_shared.utils.security import hash_password, verify_password
from app.settings.config import settings


def generate_random_token(length: int = 64) -> str:
    """Generate a cryptographically secure random token (urlsafe base64).

    Used as refresh_token for session management.
    Default length of 64 bytes produces an ~86-character string.
    """
    return secrets.token_urlsafe(length)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Encodes the provided data dict with `exp` (expiration) and `iat` (issued at)
    claims. Uses the configured JWT_SECRET_KEY and JWT_ALGORITHM.
    Default expiration is ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    The JWT payload typically includes:
    - sub: user UUID
    - email: username/email
    - roles: list of role names
    - permissions: list of permission strings
    - context: additional context (e.g., p_id)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Returns the payload dict on success.
    Raises Exception with a descriptive message if the token is expired or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
