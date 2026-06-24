# app/core/security.py

from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException
from jose import JWTError, jwt

from app.core.config import settings


def create_jwt_token(user_id: str, user_type: str) -> str:
    """
    Create a JWT token for a user.
    Guest tokens expire in 1 hour.
    Google-authenticated tokens expire in 7 days.
    """
    now = datetime.now(timezone.utc)

    if user_type == "guest":
        exp = now + timedelta(hours=1)
    else:
        exp = now + timedelta(days=7)

    payload = {
        "sub": user_id,
        "user_type": user_type,
        "exp": exp,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )


def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
        return payload
    except (JWTError, Exception):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


async def get_current_user(
    authorization: str = Header(None),
) -> dict:
    """
    FastAPI dependency that extracts and validates a Bearer token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
        )

    return verify_jwt_token(token)