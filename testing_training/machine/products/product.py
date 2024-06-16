from decimal import Decimal

from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column, composite

from testing_training.machine.database import Base
from testing_training.machine.products.money import Money


class Product(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    _amount: Mapped[Decimal] = mapped_column(init=False)
    _currency: Mapped[str] = mapped_column(init=False)
    price: Mapped[Money] = composite("_amount", "_currency")
    image: Mapped[bytes]
