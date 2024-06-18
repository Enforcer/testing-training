import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from testing_training.machine.products import list_products, Money
from testing_training.machine.inventory import (
    get_engine_with_product,
    lower_stock_on_engine,
)
from testing_training.machine.buyer_app.order import Order


class Vending:
    def __init__(self, session: Session, threadpool: ThreadPoolExecutor) -> None:
        self._session = session
        self._threadpool = threadpool

    def place_order(self, items: dict[int, int]) -> Order:
        all_products = list_products()
        product_by_id = {product.id: product for product in all_products}

        total = sum(
            product_by_id[product_id].price * quantity
            for product_id, quantity in items.items()
        )

        order = Order(
            created_at=datetime.now(),
            status="AWAITING_PAYMENT",
            total=total,
            items=items,
        )
        self._session.add(order)
        self._session.flush()

        self._threadpool.submit(
            wake_up_terminal_and_start_payment, order_id=order.id, total=total
        )
        return order

    def get_order(self, order_id: int) -> Order | None:
        stmt = select(Order).filter(Order.id == order_id)
        return self._session.execute(stmt).scalars().first()

    def timeout_orders(self, timeout: timedelta) -> None:
        stmt = (
            select(Order)
            .filter(
                Order.status == "AWAITING_PAYMENT",
                Order.created_at < datetime.now() - timeout,
            )
            .with_for_update()
        )

        orders = self._session.execute(stmt).scalars().all()
        for order in orders:
            order.status = "PAYMENT_TIMEOUT"

    def dispense_completed(self, order_id: int) -> None:
        stmt = (
            select(Order)
            .filter(
                Order.id == order_id,
            )
            .with_for_update()
        )

        order = self._session.execute(stmt).scalars().first()
        order.status = "DONE"

    def payment_successful(self, order_id: int) -> None:
        stmt = (
            select(Order)
            .filter(
                Order.id == order_id,
            )
            .with_for_update()
        )

        order = self._session.execute(stmt).scalars().first()
        order.status = "DISPENSING"

        self._session.commit()

        try:
            product_id_quantity = order.items.copy()
            for product_id, quantity in product_id_quantity.items():
                for _ in range(quantity):
                    engine_row, engine_column = get_engine_with_product(product_id)
                    print(
                        f"Dispensing {quantity} of product {product_id} from engine {engine_row}, {engine_column}"
                    )
                    fd = os.open(os.devnull, os.O_RDWR)
                    engine_controller_address = 0x02
                    drive_command = 0x13
                    engine_no = hex(engine_row * 10 + engine_column)
                    steps = hex(1)
                    frame = [engine_controller_address, drive_command, engine_no, steps]
                    frame_with_checksum = frame + [sum(frame) & 0xFF]
                    payload = bytes(frame_with_checksum)
                    os.write(fd, payload)
                    _response = os.read(fd, 1)
                    os.close(fd)
                    lower_stock_on_engine(engine_row, engine_column)
        except Exception:
            order.status = "DISPENSING_ERROR"

        self._session.commit()

        response = httpx.post(
            f"http://localhost:8000/order/{order_id}/dispense_completed"
        )
        response.raise_for_status()


def wake_up_terminal_and_start_payment(order_id: int, total: Money) -> None:
    payload = {
        "order": {
            "id": str(order_id),
            "price": {
                "currency": total.currency.name,
                "amount": str((total.amount * 100).quantize(0)),
            },
            "description": f"Payment for order #{order_id}",
        },
        "technical_info": {
            "notification_url": "http://localhost:8000/payment/notifications",
        },
    }
    transport = httpx.HTTPTransport(retries=5)
    client = httpx.Client(base_url="http://localhost:8090", transport=transport)
    response = client.post("/v1/order", json=payload)
    response.raise_for_status()
