from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from dependencies import get_bike_repo, get_brand_repo
from repositories.bike_repository import BikeRepository
from repositories.brand_repository import BrandRepository
from schemas import BikeCreate, BikeUpdate

router = APIRouter(prefix="/bikes", tags=["Велосипеды"])


@router.get("", description="Получить список велосипедов")
async def get_bikes(repository: BikeRepository = Depends(get_bike_repo)):
    bikes = await repository.get_all()
    return bikes


@router.get("/{bike_id}", description="Получить один велосипед по id")
async def get_bike_by_id(
        bike_id: int,
        repository: BikeRepository = Depends(get_bike_repo)
):
    bike = await repository.get_by_id(bike_id)
    if bike is None:
        raise HTTPException(status_code=404, detail="Велосипед не найден")
    return bike


@router.post("", description="Создать сущность велосипеда", status_code=status.HTTP_201_CREATED)
async def create_bike(
        bike_data: BikeCreate,
        repository: BikeRepository = Depends(get_bike_repo),
        brand_repository: BrandRepository = Depends(get_brand_repo)
):
    # Проверяем существование бренда
    brand = await brand_repository.get_by_id(bike_data.brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail=f"Бренд с ID {bike_data.brand_id} не найден")

    try:
        bike = await repository.create(bike_data)
        return bike
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{bike_id}", description="Удалить сущность велосипеда по id")
async def delete_bike(
        bike_id: int,
        repository: BikeRepository = Depends(get_bike_repo),
):
    result = await repository.delete(bike_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Велосипед не найден")
    return result


@router.patch("/{bike_id}", description="Отредактировать сущность велосипеда по id")
async def update_bike(
        bike_id: int,
        bike_data: BikeUpdate,
        repository: BikeRepository = Depends(get_bike_repo),
        brand_repository: BrandRepository = Depends(get_brand_repo)
):
    # Если brand_id передан, проверяем его существование
    if bike_data.brand_id is not None:
        brand = await brand_repository.get_by_id(bike_data.brand_id)
        if brand is None:
            raise HTTPException(status_code=404, detail=f"Бренд с ID {bike_data.brand_id} не найден")

    updated_bike = await repository.patch(bike_id, bike_data)
    if updated_bike is None:
        raise HTTPException(status_code=404, detail="Велосипед не найден")
    return updated_bike