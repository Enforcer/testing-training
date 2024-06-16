from collections import defaultdict

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from testing_training.machine.database import Session
from testing_training.machine.inventory.stock import Stock


class Entry(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    quantity: int


def get_inventory() -> list[Entry]:
    with Session() as session:
        stocks = session.execute(select(Stock)).scalars().all()
        quantity_by_product_id: dict[int, int] = defaultdict(int)
        for stock in stocks:
            quantity_by_product_id[stock.product_id] += stock.quantity

    return [
        Entry(product_id=product_id, quantity=quantity)
        for product_id, quantity in quantity_by_product_id.items()
    ]


def dispense(product_id: int) -> None:
    raise NotImplementedError
