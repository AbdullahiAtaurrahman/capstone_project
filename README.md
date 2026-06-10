# Course Enrollment Platform API

A secure backend API built with FastAPI for course registration, enrollment, and user management.

## Features

- JWT authentication
- Role-based access control
- Async PostgreSQL using SQLAlchemy
- Redis-backed rate limiting
- Docker Compose development setup
- Alembic migrations
- Pytest test suite

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Required Dependencies

The project installs these Python packages from `requirements.txt`:

- `fastapi`
- `uvicorn`
- `SQLAlchemy`
- `pydantic[email]`
- `pydantic-settings`
- `passlib[bcrypt]`
- `python-jose`
- `redis`
- `slowapi`
- `alembic`
- `aiosqlite`
- `email-validator`
- `python-multipart`
- `python-dotenv`
- `pytest`
- `pytest-asyncio`
- `httpx`
- `psycopg2-binary`
- `asyncpg`
- `psycopg[binary]`

### Run with Docker

```bash
git clone https://github.com/AbdullahiAtaurrahman/capstone_project.git
cd capstone_project
cp .env.example .env
docker compose up --build
```

Open:

- `http://localhost:8000`
- `http://localhost:8000/docs`

Live deployment:

- `https://capstone-project-8dn6.onrender.com`
- `https://capstone-project-8dn6.onrender.com/docs`

### Run Locally

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

```bash
docker compose exec api alembic upgrade head
```

After model changes:

```bash
docker compose exec api alembic revision --autogenerate -m "<message>"
docker compose exec api alembic upgrade head
```

## Tests

```bash
docker compose exec db psql -U postgres -c "CREATE DATABASE capstone_project_test;"
docker compose exec api pytest tests/ -v
```

## Project Structure

```text
app/
├── api/v1/          # routers
├── core/            # config, security, deps, middleware
├── models/          # database models
├── repositories/    # data access layer
├── schemas/         # Pydantic models
├── services/        # business logic
alembic/             # migrations
tests/               # automated tests
```

## Environment Variables

Copy `.env.example` to `.env` and update values.

Required variables include:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REDIS_URL`

## API Documentation

Interactive docs are available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Notes

- The app uses `EmailStr` in Pydantic schemas, so make sure `email-validator` is installed.
- Rate limiting is enabled for login to prevent abuse.

---

For API details and endpoint usage, use the FastAPI docs after starting the app.

---

# 🤝 Contributing

Contributions are welcome.

## Steps

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push changes

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

Ataur-rahman Abdullahi

GitHub: https://github.com/AbdullahiAtaurrahman

---

# ⭐ Support

If you found this project useful, consider giving it a star on GitHub.
