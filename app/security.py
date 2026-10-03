"""Small stdlib-only bearer-token and password helpers for the account API."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import UserModel

SECRET_KEY = os.getenv("APP_SECRET_KEY", "development-only-change-me")
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 14


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
    return f"{_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_text, digest_text = encoded.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
        expected = base64.urlsafe_b64decode(digest_text + "=" * (-len(digest_text) % 4))
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: str) -> str:
    now = int(time.time())
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode(json.dumps({"sub": user_id, "iat": now, "exp": now + TOKEN_TTL_SECONDS}, separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}"
    signature = _encode(hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def decode_access_token(token: str) -> Optional[str]:
    try:
        header, payload, signature = token.split(".")
        signing_input = f"{header}.{payload}"
        expected = _encode(hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        payload_bytes = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = json.loads(payload_bytes)
        if int(data.get("exp", 0)) <= int(time.time()):
            return None
        return str(data["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


async def get_optional_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserModel]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    user_id = decode_access_token(token) if scheme.lower() == "bearer" else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return user


async def get_current_user(user: Optional[UserModel] = Depends(get_optional_user)) -> UserModel:
    if not user:
        raise HTTPException(status_code=401, detail="Sign in to continue")
    return user
