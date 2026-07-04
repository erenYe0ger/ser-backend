# app/core/security.py

from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException, Request
from jose import JWTError, jwt
from slowapi.util import get_remote_address

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


def get_rate_limit_key(request: Request) -> str:
    """
    Return a rate-limit key for the request.

    Priority:
    1. Authenticated non-guest user -> user:<user_id>
    2. Fallback -> ip:<client_ip>

    Never raises an exception.
    """
    try:
        authorization = request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()

            if token:
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=["HS256"],
                )

                # Treat guest tokens like unauthenticated clients
                if payload.get("user_type") != "guest":
                    sub = payload.get("sub")
                    if sub:
                        return f"user:{sub}"
    except Exception:
        pass

    ip = get_remote_address(request) or "unknown"
    return f"ip:{ip}"


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