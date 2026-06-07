import os
import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.core.db_async import Base
from app.core.deps import get_async_db, rate_limit
from app.repositories import course_repository
from app.api.v1 import health as health_module
from app.repositories import user_repository
from app.services import auth_service

# Ensure application settings are loaded from test-safe environment values.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("DATABASE_URL", "sqlite:///./app.db")
os.environ.setdefault("DATABASE_URL_ASYNC", "sqlite+aiosqlite:///./app.db")
os.environ.setdefault("ENVIRONMENT", "TEST")

from app.main import app as fastapi_app  # noqa: E402


class DummyRedis:
    async def ping(self) -> bool:
        return True


async def _fake_cache_get(key: str):
    return None


async def _fake_cache_set(key: str, value, ttl: int = 60):
    return None


async def _fake_cache_delete_pattern(pattern: str):
    return None


async def _fake_get_redis():
    return DummyRedis()


@pytest.fixture(scope="session")
def test_app(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    database_url = f"sqlite+aiosqlite:///{db_file}"
    engine = create_async_engine(database_url, echo=False, future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())

    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as db:
            yield db

    async def _fake_rate_limit(request: Request, max_calls: int = 5, window: int = 60):
        return None

    fastapi_app.dependency_overrides[get_async_db] = override_get_async_db
    fastapi_app.dependency_overrides[rate_limit] = _fake_rate_limit

    course_repository.cache_get = _fake_cache_get
    course_repository.cache_set = _fake_cache_set
    course_repository.cache_delete_pattern = _fake_cache_delete_pattern
    health_module.get_redis = _fake_get_redis

    user_repository.hash_password = lambda plain: plain
    auth_service.verify_password = lambda plain, hashed: plain == hashed

    return fastapi_app


@pytest.fixture(scope="session")
def client(test_app):
    with TestClient(test_app) as client:
        yield client
