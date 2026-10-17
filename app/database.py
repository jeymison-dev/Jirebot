from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

# 1. Configurau00e7u00e3o do caminho e driver assu00edncrono
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'jirebot.db')}"

# 2. Inicializau00e7u00e3o do motor assu00edncrono
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Fu00e1brica de sessu00f5es assu00edncronas
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession  # Garante que a sessu00e3o seja estritamente assu00edncrona
)

# 4. Gerador de escopo do banco de dados para o FastAPI (Padru00e3o Su00eanior)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# 5. Classe Base declarativa padru00e3o


class Base(DeclarativeBase):
    __abstract__ = True
    __slots__ = ()
