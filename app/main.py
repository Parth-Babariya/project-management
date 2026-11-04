from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db
from app.core.exceptions import AppException, app_exception_handler
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Anything after yield runs at shutdown



app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend for user authentication, project management and image uploads.",
    lifespan=lifespan,
)
app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth.router)



@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Confirms the API is running and the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unavailable"},
        )
    return {"status": "ok", "database": "connected"}