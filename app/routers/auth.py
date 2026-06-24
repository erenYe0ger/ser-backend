# app/routers/auth.py

import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_jwt_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleAuthRequest(BaseModel):
    token: str


@router.post("/google")
async def google_auth(
    payload: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        token_info = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            payload.token,
            Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token",
        )

    user_id = token_info["sub"]
    email = token_info.get("email")
    name = token_info.get("name")
    picture = token_info.get("picture")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.name = name
        user.picture = picture
        # Keep email updated in case it changes
        user.email = email
    else:
        user = User(
            id=user_id,
            email=email,
            name=name,
            picture=picture,
            user_type="google",
        )
        db.add(user)

    await db.commit()

    return {
        "access_token": create_jwt_token(user_id, "google"),
        "user_type": "google",
        "name": name,
        "email": email,
        "picture": picture,
    }


@router.post("/guest")
async def guest_auth(
    db: AsyncSession = Depends(get_db),
):
    guest_id = str(uuid.uuid4())

    user = User(
        id=guest_id,
        email=None,
        name=None,
        picture=None,
        user_type="guest",
    )

    db.add(user)
    await db.commit()

    return {
        "access_token": create_jwt_token(guest_id, "guest"),
        "user_type": "guest",
    }