from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from models import BikeTable
from schemas import BikeCreate, BikeUpdate


class BikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[BikeTable]:
        result = await self.session.execute(select(BikeTable))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> BikeTable:
        result = await self.session.execute(
            select(BikeTable).where(BikeTable.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, bike_data: BikeCreate) -> BikeTable:
        bike = BikeTable(**bike_data.model_dump())
        self.session.add(bike)
        await self.session.commit()
        await self.session.refresh(bike, ["brand"])
        return bike

    async def delete(self, bike_id: int):
        bike = await self.get_by_id(bike_id)
        if not bike:
            return None
        await self.session.delete(bike)
        await self.session.commit()
        return {"status": "success"}

    async def patch(self, bike_id: int, bike_data: BikeUpdate) -> BikeTable | None:
        bike = await self.get_by_id(bike_id)
        if not bike:
            return None
        data = bike_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(bike, key, value)

        await self.session.commit()
        await self.session.refresh(bike)
        return bike
