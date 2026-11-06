# Project Management Backend

A REST API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy** and **Alembic** for user authentication, project management and project image uploads.

---

## Features

- User registration and login with **JWT** authentication
- Passwords stored as **bcrypt** hashes, never in plain text
- Protected endpoints: only authenticated users can manage projects
- Users can only view, edit or delete **their own** projects
- Project CRUD (create, list, view, update, delete)
- Filter projects by **category** and **tags**
- **Paginated** project listing
- Upload **multiple images** per project, list them, and download them through an authenticated endpoint
- Database schema managed with **Alembic** migrations
- All configuration through **environment variables**


---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | PostgreSQL 18 (Docker) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Validation | Pydantic v2, pydantic-settings |
| Auth | PyJWT, bcrypt |
| Server | Uvicorn |

---

## Project Structure

```
project-management/
├── app/
│   ├── main.py              # FastAPI app, router registration, error handlers
│   ├── core/
│   │   ├── config.py        # Settings loaded from .env
│   │   ├── security.py      # Password hashing, JWT create/verify
│   │   └── exceptions.py    # Custom exceptions and global error handlers
│   ├── database/
│   │   ├── base.py          # SQLAlchemy declarative Base
│   │   └── connection.py    # Engine and session factory
│   ├── models/              # SQLAlchemy models (User, Project, ProjectImage)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   ├── repositories/        # Database queries
│   ├── dependencies/        # get_db, get_current_user
│   └── uploads/projects/    # Uploaded images (not committed)
├── alembic/                 # Migration scripts
├── tests/                   # pytest test suite
├── .env.example             # Template for environment variables
├── alembic.ini
├── pytest.ini
└── requirements.txt
```

**Request flow:** `router` -> `service` (business rules) -> `repository` (database) -> `model`

---

## Database Design

```
users  1 ──── N  projects  1 ──── N  project_images
```

| Table | Key columns |
|---|---|
| `users` | id, name, email (unique), hashed_password, created_at |
| `projects` | id, title, description, category, tags (text array, GIN index), owner_id -> users, created_at, updated_at |
| `project_images` | id, project_id -> projects, file_path, original_filename, content_type, file_size, uploaded_at |

- Deleting a user deletes their projects; deleting a project deletes its images (`ON DELETE CASCADE`).
- Images are stored on disk; the database stores only the file path and metadata.

---

## Prerequisites

- **Python 3.11+**
- **Docker Desktop** (for PostgreSQL), or a local PostgreSQL installation
- **Git**

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Parth-Babariya/project-management.git
cd project-management
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

> If PowerShell blocks the script, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL in Docker

Make sure Docker Desktop is running, then:

```bash
docker run -d --name project-management-db \
  -e POSTGRES_USER=pm_user \
  -e POSTGRES_PASSWORD=change_me \
  -e POSTGRES_DB=project_mgmt \
  -p 5432:5432 \
  -v project-management-pgdata:/var/lib/postgresql \
  --restart unless-stopped \
  postgres:18
```

**Windows (PowerShell)**, same command on one line:
```powershell
docker run -d --name project-management-db -e POSTGRES_USER=pm_user -e POSTGRES_PASSWORD=change_me -e POSTGRES_DB=project_mgmt -p 5432:5432 -v project-management-pgdata:/var/lib/postgresql --restart unless-stopped postgres:18
```

Check it is running:
```bash
docker ps
```

> Using a local PostgreSQL instead? Create the user and database manually:
> ```sql
> CREATE USER pm_user WITH PASSWORD 'change_me';
> CREATE DATABASE project_mgmt OWNER pm_user;
> ```

### 5. Configure environment variables

Copy the template:

```bash
cp .env.example .env          # macOS / Linux
Copy-Item .env.example .env   # Windows
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env`:
```dotenv
APP_NAME=Project Management API
DATABASE_URL=postgresql+psycopg2://pm_user:change_me@localhost:5432/project_mgmt
SECRET_KEY=<paste-generated-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_UPLOAD_SIZE_MB=5
MAX_IMAGES_PER_UPLOAD=10
PUBLIC_UPLOADS=false
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (required) |
| `SECRET_KEY` | Key used to sign JWT tokens (required) |
| `ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |
| `MAX_UPLOAD_SIZE_MB` | Maximum size of one image |
| `MAX_IMAGES_PER_UPLOAD` | Maximum number of images in one request |
| `PUBLIC_UPLOADS` | `true` also serves files publicly at `/uploads/...` (off by default) |

> Use only letters, digits and `_` in the password; characters like `@ : / # %` break the URL.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
python -m uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| http://127.0.0.1:8000/docs | Swagger UI (interactive) |
| http://127.0.0.1:8000/redoc | ReDoc documentation |
| http://127.0.0.1:8000/health | Health check (API + database) |

---

## API Endpoints

### Health
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | API and database status |

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register with name, email, password |
| POST | `/auth/login` | No | Login with email and password (JSON), returns JWT |
| POST | `/auth/token` | No | OAuth2 form login (used by Swagger "Authorize") |
| GET | `/auth/me` | Yes | Current user's profile |

### Projects
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/projects` | Yes | Create a project |
| GET | `/projects` | Yes | List my projects (filters + pagination) |
| GET | `/projects/{id}` | Yes | Project details |
| PATCH | `/projects/{id}` | Yes | Partial update (only fields sent change) |
| DELETE | `/projects/{id}` | Yes | Delete a project and its images |

**List query parameters**

| Parameter | Example | Description |
|---|---|---|
| `page` | `1` | Page number (starts at 1) |
| `size` | `10` | Items per page (1-100) |
| `category` | `bridges` | Exact match, case-insensitive |
| `tags` | `steel,urgent` or `tags=steel&tags=urgent` | Filter by tags |
| `tag_match` | `all` | `any` (default) = at least one tag, `all` = every tag |

Response:
```json
{ "items": [ ... ], "total": 13, "page": 1, "size": 10, "pages": 2 }
```

Example: `GET /projects?category=bridges&tags=steel,urgent&tag_match=all&page=1&size=5`

### Images
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/projects/{id}/images` | Yes | Upload 1-10 images (multipart, field name `files`). All-or-nothing |
| GET | `/projects/{id}/images` | Yes | List a project's images (each has a `url`) |
| GET | `/projects/{id}/images/{image_id}/file` | Yes | Download an image (owner only) |

Allowed types: JPEG, PNG, WEBP. The real file type is checked from the file's first bytes, not just its name.

### Status codes

| Code | Meaning |
|---|---|
| 200 / 201 / 204 | Success / created / deleted |
| 400 | Empty file, or too many files in one upload |
| 401 | Missing, invalid or expired token; wrong credentials |
| 403 | Accessing another user's project |
| 404 | Project or image not found |
| 409 | Email already registered |
| 413 | Image larger than `MAX_UPLOAD_SIZE_MB` |
| 415 | Not a JPEG, PNG or WEBP image |
| 422 | Request validation failed |
| 500 | Unexpected server error (details are logged, never returned) |
| 503 | Database unavailable |

Every error returns JSON with a `detail` field. Validation errors (422) also include a list of problems:
```json
{
  "detail": "Validation failed",
  "errors": [{ "field": "password", "message": "Password must contain at least one letter and one digit" }]
}
```

---

## Using the API from Swagger

1. Open http://127.0.0.1:8000/docs
2. **POST `/auth/register`** to create a user
3. Click **Authorize** (top right) and enter your email as *username* and your password
4. All protected endpoints now send the token automatically

Swagger forgets the token when the page is refreshed, so authorize again after a refresh.

---



## Common Commands

### Server
```bash
python -m uvicorn app.main:app --reload   # start (auto-reload on save)
```

### Database (Docker)
```bash
docker start project-management-db        # start
docker stop project-management-db         # stop
docker ps                                 # check status
docker exec -it project-management-db psql -U pm_user -d project_mgmt   # open psql
```

Useful psql commands: `\dt` (tables), `\d projects` (table details), `\q` (quit).

### Migrations
```bash
alembic upgrade head                      # apply all migrations
alembic current                           # show current revision
alembic history                           # list all revisions
alembic downgrade -1                      # roll back one migration
```

After changing a model:
```bash
alembic revision --autogenerate -m "describe the change"
# review the new file in alembic/versions/ before applying
alembic upgrade head
```

---

## Design Decisions

- **Layered architecture:** router -> service -> repository -> model. Each layer has one job and can be tested alone.
- **Tags as a PostgreSQL array with a GIN index:** simple, no join table, and fast for "any/all tags" filtering.
- **Ownership:** every project and image endpoint checks that the project belongs to the logged-in user (403 otherwise). The owner comes from the token, never from the request body.
- **Images on disk, metadata in the database:** files get random UUID names; the original name is only stored for display.
- **Authenticated downloads:** images are served through a protected endpoint. `PUBLIC_UPLOADS=true` optionally exposes `/uploads/...` publicly (off by default, intended only for non-sensitive images).
- **All-or-nothing uploads:** every file is validated (type, size, real content) before any is saved.
- **Security details:** same error for wrong email and wrong password, a dummy hash check to equalise timing, a database unique index as a backstop for duplicate emails, and a pinned JWT algorithm.
- **Consistent errors:** every error returns JSON with a `detail` field; unexpected errors never leak stack traces.

## Production Considerations

- Store images in object storage (S3, GCS or R2) behind a CDN, using short-lived presigned URLs.
- Generate thumbnails and scan uploads in a background worker.
- Add rate limiting on login, refresh tokens, and HTTPS.

---

## Troubleshooting

| Problem | Cause / Fix |
|---|---|
| `Connection refused` on port 5432 | Docker Desktop or the container is not running. Start Docker Desktop, then `docker start project-management-db`. |
| `failed to connect to the docker API ... dockerDesktopLinuxEngine` | Docker Desktop is not running. Open it and wait for "Engine running". |
| App connects to the wrong database | A system environment variable overrides `.env` (environment variables take priority). Check with `echo $env:DATABASE_URL` (PowerShell) or `echo $DATABASE_URL`, and remove it. |
| `password authentication failed` | Password in `DATABASE_URL` does not match the database user's password. |
| `ModuleNotFoundError: No module named 'app'` | Run commands from the project root with the virtual environment active. |
| Alembic: `No changes detected` | Models not imported in `alembic/env.py` (`import app.models`). |
| Port 8000 already in use | Another app or container is using it. Stop it, or run with `--port 8001`. |
| Swagger returns 401 on protected endpoints | Click **Authorize** again; the token is lost when the page refreshes. |
| Prompt shows `(venv) (base)` | Conda base is also active. Run `conda config --set auto_activate_base false` and reopen the terminal. |

---

## Security Notes

- `.env` is listed in `.gitignore` and must never be committed. Use `.env.example` as the template.
- Passwords are hashed with bcrypt before storage.
- JWT tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Uploaded files are renamed with random UUIDs; original filenames are never used as paths.
- Uploads are limited by type, real content, size and count.