from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite (development)
DATABASE_URL = "sqlite:///./app.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=True,  # Logs SQL — disable in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Modern Base class (SQLAlchemy 2.x)
class Base(DeclarativeBase):
    pass
