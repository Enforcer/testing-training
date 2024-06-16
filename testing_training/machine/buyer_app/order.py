from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column, composite

from testing_training.machine.database import Base
from testing_training.machine.products import Money


class Order(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column()
    status: Mapped[Literal["AWAITING_PAYMENT", "DISPENSING", "DONE", "PAYMENT_TIMEOUT", "DISPENSING_ERROR"]]
    _amount: Mapped[Decimal] = mapped_column(init=False)
    _currency: Mapped[str] = mapped_column(init=False)
    total: Mapped[Money] = composite("_amount", "_currency")
    items: Mapped[dict[int, int]] = mapped_column(JSON)
