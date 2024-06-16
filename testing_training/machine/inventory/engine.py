from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column

from testing_training.machine.database import Base


class Engine(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "engines"

    row: Mapped[int] = mapped_column(primary_key=True)
    column: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int | None] = mapped_column(ForeignKey("stocks.id"))
