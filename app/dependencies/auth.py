from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# Reads "Authorization: Bearer <token>" from the request.
# tokenUrl tells Swagger's Authorize button where to log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired") from None
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid authentication token") from None

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid authentication token")

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise UnauthorizedError("Invalid authentication token") from None

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user


# Shortcut for endpoints: `current_user: CurrentUser`
CurrentUser = Annotated[User, Depends(get_current_user)]