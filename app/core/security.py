from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


# ---------- Password hashing ----------

def hash_password(password: str) -> str:
    """Return a bcrypt hash of the password (salt is generated and stored inside the hash)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # Malformed hash or password longer than bcrypt's 72-byte limit
        return False


# ---------- JWT ----------

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT. `subject` is the user id."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(subject),   # JWT spec: subject must be a string
        "iat": now,            # issued at
        "exp": expire,         # expiry, checked automatically on decode
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Verify signature and expiry, return the payload.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError if the token is bad.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"require": ["exp", "sub"]},
    )