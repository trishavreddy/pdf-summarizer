from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Handle SQLite vs PostgreSQL connection args
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(settings.database_url, echo=True, connect_args=connect_args)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
