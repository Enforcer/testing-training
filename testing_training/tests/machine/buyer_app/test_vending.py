import time
from pathlib import Path
from typing import Callable

import httpx
from sqlalchemy import create_engine

from testing_training.machine.buyer_app.vending import Vending
from testing_training.machine.database import Base, Session
from testing_training.machine.inventory.engine import Engine
from testing_training.machine.inventory.stock import Stock
from testing_training.machine.products import add_product, Money, list_products
from testing_training.machine.products.money import Currency
from testing_training.tests.machine.buyer_app import tools


def test_order_succeeds() -> None:
    wait_until(terminal_app_is_running)

    tools.restore_engine_state()
    tools.restore_terminal()

    sqlite_file = Path(__file__).parent / "test_db.db"
    Session.remove()
    engine = create_engine(f"sqlite:///{sqlite_file}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    add_product(
        name="Dress",
        description="Nice dress",
        price=Money(10, Currency.PLN),
        image=b"image",
    )
    products = list_products()
    product_id = products[0].id
    session = Session()
    stock_1 = Stock(product_id=product_id, quantity=1)
    session.add(stock_1)
    session.flush()
    engine_1 = Engine(row=1, column=1, stock_id=stock_1.id)
    session.add(engine_1)
    session.commit()

    vending = Vending(session=session)
    order = vending.place_order(items={product_id: 1})  # order 1 piece of product
    order_id = order.id
    session.commit()

    def wait_until_order_completed() -> bool:
        session.rollback()
        order = vending.get_order(order_id=order_id)
        return order.status == "DONE"

    wait_until(wait_until_order_completed, timeout=10)


def test_order_fails_when_payment_terminal_malfunctions() -> None:
    wait_until(terminal_app_is_running)

    tools.restore_engine_state()
    tools.restore_terminal()

    sqlite_file = Path(__file__).parent / "test_db.db"
    Session.remove()
    engine = create_engine(f"sqlite:///{sqlite_file}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    tools.simulate_terminal_malfunction()

    add_product(
        name="Socks",
        description="A pair of socks",
        price=Money(9, Currency.PLN),
        image=b"image",
    )
    products = list_products()
    product_id = products[0].id
    session = Session()
    stock_1 = Stock(product_id=product_id, quantity=1)
    session.add(stock_1)
    session.flush()
    engine_1 = Engine(row=1, column=1, stock_id=stock_1.id)
    session.add(engine_1)
    session.commit()

    vending = Vending(session=session)
    order = vending.place_order(items={product_id: 1})  # order 1 piece of product

    assert order.status == "PAYMENT_FAILED"


def wait_until(condition: Callable[[], bool], timeout: int = 5) -> None:
    """Waits until condition is met"""
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if condition():
            return
        time.sleep(0.1)
    raise TimeoutError(f"Condition {condition.__name__} was not met in time!")


def terminal_app_is_running() -> bool:
    try:
        response = httpx.get("http://localhost:8090/v1/healthcheck")
    except httpx.HTTPError:
        return False
    else:
        return response.status_code in (200, 500)
