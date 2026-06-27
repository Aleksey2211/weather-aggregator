from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column, relationship
import os
from sqlalchemy import ARRAY, String, DateTime, ForeignKey
from typing import AsyncGenerator
from configs import DATABASE_URL
from datetime import datetime, timedelta, timezone




engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    #echo=False,
    pool_size=10,  # Размер пула соединений
    max_overflow=20,  # Максимальное количество соединений сверх pool_size
    future=True,
)

#Session fabric
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
)

#Generator of sessions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

"""Root class for DB_tables"""
class Base(DeclarativeBase):
    pass



