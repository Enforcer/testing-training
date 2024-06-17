from collections import defaultdict

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from testing_training.machine.database import Session
from testing_training.machine.inventory.engine import Engine
from testing_training.machine.inventory.stock import Stock


class Entry(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    quantity: int


def get_inventory() -> list[Entry]:
    session = Session()
    stocks = session.execute(select(Stock)).scalars().all()
    quantity_by_product_id: dict[int, int] = defaultdict(int)
    for stock in stocks:
        quantity_by_product_id[stock.product_id] += stock.quantity

    return [
        Entry(product_id=product_id, quantity=quantity)
        for product_id, quantity in quantity_by_product_id.items()
    ]


def get_engine_with_product(product_id: int) -> tuple[int, int]:
    session = Session()
    stmt = select(Stock).filter(Stock.product_id == product_id, Stock.quantity > 0)
    stock = session.execute(stmt).scalars().first()
    engine = (
        session.execute(select(Engine).filter(Engine.stock_id == stock.id))
        .scalars()
        .first()
    )
    return engine.row, engine.column


def lower_stock_on_engine(row: int, column: int) -> None:
    session = Session()
    stmt = select(Engine).filter(Engine.row == row, Engine.column == column)
    engine = session.execute(stmt).scalars().first()
    stock = (
        session.execute(select(Stock).filter(Stock.id == engine.stock_id))
        .scalars()
        .first()
    )
    stock.quantity = stock.quantity - 1
