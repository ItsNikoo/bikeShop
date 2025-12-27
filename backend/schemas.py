import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from sqlalchemy import null


class BikeBase(BaseModel):
    brand: str
    model: str
    year: int
    description: Optional[str] = None


class BikeCreate(BaseModel):
    brand: str
    model: str
    year: int
    description: Optional[str] = None

    @field_validator("year")
    @classmethod
    def year_validator(cls, v):
        if not (2019 <= v <= datetime.datetime.now().year):
            raise ValueError("Невалидный год выпуска велосипеда")
        return v


class BikeUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None

    @field_validator("year")
    @classmethod
    def year_validator(cls, v):
        if v is not None:
            if not (2019 <= v <= datetime.datetime.now().year):
                raise ValueError("Невалидный год выпуска велосипеда")
        return v


class Bike(BikeCreate):
    id: int
