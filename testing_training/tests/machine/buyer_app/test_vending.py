import time
from typing import Callable

import httpx

from testing_training.machine.buyer_app.vending import Vending
from testing_training.machine.database import Session
from testing_training.machine.inventory.engine import Engine
from testing_training.machine.inventory.stock import Stock
from testing_training.machine.inventory import set_stock_on_engine
from testing_training.machine.products import add_product, Money, list_products
from testing_training.machine.products.money import Currency
from testing_training.tests.machine.buyer_app import tools


def test_order_succeeds() -> None:
    wait_until(terminal_app_is_running)

    tools.restore_engine_state()
    tools.restore_terminal()

    add_product(
        name="Dress",
        description="Nice dress",
        price=Money(10, Currency.PLN),
        image=b"image",
    )
    products = list_products()
    product_id = products[0].id
    set_stock_on_engine(row=1, column=1, product_id=product_id, quantity=1)

    vending = Vending()
    order = vending.place_order(items={product_id: 1})  # order 1 piece of product
    order_id = order.id
    Session().commit()

    def wait_until_order_completed() -> bool:
        order = vending.get_order(order_id=order_id)
        return order.status == "DONE"

    wait_until(wait_until_order_completed, timeout=10)


def test_order_fails_when_payment_terminal_malfunctions() -> None:
    wait_until(terminal_app_is_running)

    tools.restore_engine_state()
    tools.restore_terminal()

    tools.simulate_terminal_malfunction()

    add_product(
        name="Socks",
        description="A pair of socks",
        price=Money(9, Currency.PLN),
        image=b"image",
    )
    products = list_products()
    product_id = products[0].id
    set_stock_on_engine(row=1, column=1, product_id=product_id, quantity=1)

    vending = Vending()
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
