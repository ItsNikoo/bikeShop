import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

# Схемы для Brand
class BrandBase(BaseModel):
    name: str
    description: str
    country: str


class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None


class Brand(BrandBase):
    id: int

    class Config:
        from_attributes = True


# Схемы для Bike
class BikeBase(BaseModel):
    brand_id: int
    model: str
    year: int
    description: Optional[str] = None

    @field_validator("year")
    @classmethod
    def year_validator(cls, v):
        if not (2019 <= v <= datetime.datetime.now().year):
            raise ValueError("Невалидный год выпуска велосипеда")
        return v


class BikeCreate(BikeBase):
    pass


class BikeUpdate(BaseModel):
    brand_id: Optional[int] = None
    model: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None

    @field_validator("brand_id")
    @classmethod
    def validate_brand_id(cls, v: Optional[int]):
        if v is not None:
            # Простая проверка - больше 0
            if v <= 0:
                raise ValueError("ID бренда должен быть положительным числом")
        return v

    @field_validator("year")
    @classmethod
    def year_validator(cls, v):
        if v is not None:
            if not (2019 <= v <= datetime.datetime.now().year):
                raise ValueError("Невалидный год выпуска велосипеда")
        return v


class Bike(BikeBase):
    id: int
    brand: Brand  # Включаем информацию о бренде

    class Config:
        from_attributes = True