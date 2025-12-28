from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import BrandTable
from schemas import BrandCreate, BrandUpdate


class BrandRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[BrandTable]:
        result = await self.session.execute(select(BrandTable))
        return result.scalars().all()

    async def get_by_id(self, brand_id: int) -> BrandTable:
        result = await self.session.execute(
            select(BrandTable).where(BrandTable.id == brand_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: BrandCreate) -> BrandTable:
        brand = BrandTable(**data.model_dump())
        self.session.add(brand)
        await self.session.commit()
        await self.session.refresh(brand)
        return brand

    async def delete(self, brand_id: int):
        brand = await self.get_by_id(brand_id)
        if not brand:
            return None
        await self.session.delete(brand)
        await self.session.commit()
        return {"status": "success"}

    async def patch(self, brand_id: int, brand_data: BrandUpdate) -> BrandTable | None:
        brand = await self.get_by_id(brand_id)
        if not brand:
            return None
        data = brand_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(brand, key, value)

        await self.session.commit()
        await self.session.refresh(brand)
        return brand
