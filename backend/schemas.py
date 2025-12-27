from typing import Optional

from pydantic import BaseModel


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


class BikeUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None


class Bike(BikeCreate):
    id: int
