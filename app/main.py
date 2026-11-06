from contextlib import asynccontextmanager
import logging


from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError


from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db
from app.routers import auth, image, project
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)


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


register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(image.router)

# Serve uploaded files at /uploads/<project_id>/<file>
if settings.PUBLIC_UPLOADS:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # must exist before mounting
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")



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