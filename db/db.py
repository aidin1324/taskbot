from contextlib import asynccontextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import get_settings

setting = get_settings()

engine = create_async_engine(setting.database_url, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()


@asynccontextmanager
async def get_session() -> AsyncSession: # type: ignore
    async with SessionLocal() as session:
        yield session
        