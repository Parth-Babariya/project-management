Step 0: Setup

powershell
docker start project-management-db
docker ps
docker exec -it project-management-db psql -U postgres -c "CREATE USER pm_user WITH PASSWORD 'Pm_Local_2026';"
docker exec -it project-management-db psql -U postgres -c "CREATE DATABASE project_mgmt OWNER pm_user;"

python --version
python -m venv venv
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary alembic pydantic-settings email-validator pyjwt bcrypt python-multipart pytest httpx
python -m pip freeze > requirements.txt


Step 1: Config

powershell
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from app.core.config import settings; print(settings.DATABASE_URL); print(settings.UPLOAD_DIR); print(len(settings.SECRET_KEY))"

Step 2: Database connection

powershell
python -c "from sqlalchemy import text; from app.database.connection import engine; c = engine.connect(); print(c.execute(text('SELECT current_user, current_database(), version()')).fetchone()); c.close()"

Step 3: Models

powershell
python -c "from sqlalchemy.orm import configure_mappers; import app.models; from app.d