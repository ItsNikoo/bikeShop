from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Model

engine = create_async_engine(
    "sqlite+aiosqlite:///bikes.db"
)

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
