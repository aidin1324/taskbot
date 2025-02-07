from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import get_setting

setting = get_setting()

engine = create_async_engine(setting.database_url, echo=True)

Base = declarative_base()
