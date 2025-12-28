from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from pydantic import ValidationError

from dependencies import get_brand_repo
from repositories.brand_repository import BrandRepository
from schemas import BrandCreate, BrandUpdate

router = APIRouter(prefix="/brands", tags=["Бренды"])


@router.get("", description="Получить все бренды")
async def get_brands(repository: BrandRepository = Depends(get_brand_repo)):
    brands = await repository.get_all()
    return brands


@router.get("/{brand_id}", description="Получить один бренд по id")
async def get_brand_by_id(brand_id: int, repository: BrandRepository = Depends(get_brand_repo)):
    brand = await repository.get_by_id(brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    return brand


@router.post("", description="Создать сущность бренда", status_code=status.HTTP_201_CREATED)
async def create_brand(data: BrandCreate, repository: BrandRepository = Depends(get_brand_repo)):
    try:
        brand = await repository.create(data)
        return brand
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.json())


@router.delete("/{brand_id}", description="Удалить бренд по id")
async def delete_brand(brand_id: int, repository: BrandRepository = Depends(get_brand_repo)):
    result = await repository.delete(brand_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    return result


@router.patch("/{brand_id}", description="Отредактировать сущность бренда по id")
async def update_brand(
        brand_id: int,
        brand_data: BrandUpdate,
        repository: BrandRepository = Depends(get_brand_repo),
):
    updated_brand = await repository.patch(brand_id, brand_data)
    if updated_brand is None:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    return updated_brand
