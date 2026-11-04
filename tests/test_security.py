from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plain_text():
    hashed = hash_password("Secret123")
    assert hashed != "Secret123"
    assert hashed.startswith("$2b$")


def test_verify_correct_and_wrong_password():
    hashed = hash_password("Secret123")
    assert verify_password("Secret123", hashed) is True
    assert verify_password("wrong-pass", hashed) is False


def test_same_password_gives_different_hashes():
    assert hash_password("Secret123") != hash_password("Secret123")


def test_token_round_trip():
    token = create_access_token(42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_expired_token_is_rejected():
    token = create_access_token(1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_token_signed_with_other_key_is_rejected():
    fake = jwt.encode({"sub": "1", "exp": 9999999999}, "not-the-real-key", algorithm=settings.ALGORITHM)
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(fake)