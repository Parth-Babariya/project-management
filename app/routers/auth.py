from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    return service.register(data)


@router.post("/login", response_model=Token, summary="Login with email and password (JSON)")
def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return service.login(data.email, data.password)


@router.post("/token", response_model=Token, summary="OAuth2 login (used by Swagger Authorize)")
def login_for_swagger(
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    # Swagger sends the email in the "username" field
    return service.login(form.username, form.password)



@router.get("/me", response_model=UserResponse, summary="Get the logged-in user")
def read_current_user(current_user: CurrentUser):
    return current_user