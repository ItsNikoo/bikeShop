from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Model(DeclarativeBase):
    pass


class BrandTable(Model):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    country: Mapped[str]

    # Связь с велосипедами
    bikes: Mapped[List["BikeTable"]] = relationship(back_populates="brand")


class BikeTable(Model):
    __tablename__ = "bikes"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    model: Mapped[str]
    year: Mapped[int]
    description: Mapped[Optional[str]]

    brand: Mapped["BrandTable"] = relationship(back_populates="bikes")
