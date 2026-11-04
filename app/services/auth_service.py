from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate

# Used when the email doesn't exist, so the response takes the same time
# as a wrong password (prevents guessing which emails are registered).
_DUMMY_HASH = hash_password("dummy-password-for-timing")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("Email is already registered")
        try:
            return self.users.create(
                name=data.name,
                email=data.email,
                hashed_password=hash_password(data.password),
            )
        except IntegrityError:
            # Two simultaneous sign-ups with the same email: the DB unique index catches it
            self.db.rollback()
            raise ConflictError("Email is already registered")

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email.lower())
        if user is None:
            verify_password(password, _DUMMY_HASH)
            raise UnauthorizedError("Incorrect email or password")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        return user

    def login(self, email: str, password: str) -> Token:
        user = self.authenticate(email, password)
        return Token(
            access_token=create_access_token(user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )