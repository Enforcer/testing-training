from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column

from testing_training.machine.database import Base


class Stock(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
