from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from dependencies import get_bike_repo
from repositories.bike_repository import BikeRepository
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


@router.post("", description="Создать сущность велосипеда")
async def create_bike(
        bike_data: BikeCreate,
        repository: BikeRepository = Depends(get_bike_repo)
):
    try:
        bike = await repository.create(bike_data)
        return bike
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e)


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
):
    updated_bike = await repository.patch(bike_id, bike_data)
    if updated_bike is None:
        raise HTTPException(status_code=404, detail="Велосипед не найден")
    return updated_bike
