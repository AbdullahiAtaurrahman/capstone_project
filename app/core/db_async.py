from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

DATABASE_URL_ASYNC = settings.DATABASE_URL_ASYNC
# PostgreSQL async: "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
