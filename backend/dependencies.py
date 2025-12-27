from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import new_session
from repositories.bike_repository import BikeRepository

# Зависимость для сессии базы данных
async def get_db() -> AsyncSession:
    async with new_session() as session:
        yield session

# Зависимость для репозитория велосипедов
async def get_bike_repo(db: AsyncSession = Depends(get_db)) -> BikeRepository:
    """Dependency, возвращающая репозиторий с привязанной сессией"""
    return BikeRepository(db)
