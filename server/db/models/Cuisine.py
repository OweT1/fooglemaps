from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class Cuisine(Base):
    __tablename__ = "cuisines"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
