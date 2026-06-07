from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.db import SessionLocal
from app.core.db_async import AsyncSessionLocal


# Synchronous
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async
async def get_db_async():
    async with AsyncSessionLocal() as db:
        yield db
