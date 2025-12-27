from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    pass


class BikeTable(Model):
    __tablename__ = "bikes"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str]
    model: Mapped[str]
    year: Mapped[int]
    description: Mapped[Optional[str]]