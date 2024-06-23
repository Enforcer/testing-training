import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import cast

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from testing_training.machine.database import Session as MachineSession

from testing_training.machine.products import list_products, Money
from testing_training.machine.inventory import (
    get_engine_with_product,
    lower_stock_on_engine,
)
from testing_training.machine.buyer_app.order import Order
from testing_training.myserial import Serial, ACK, NACK


logger = logging.getLogger(__name__)


class Vending:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session or MachineSession()
        self._threadpool = ThreadPoolExecutor(max_workers=4)

    def place_order(self, items: dict[int, int]) -> Order:
        all_products = list_products()
        product_by_id = {product.id: product for product in all_products}

        total = sum(
            product_by_id[product_id].price * quantity
            for product_id, quantity in items.items()
        )
        total = cast(Money, total)

        order = Order(
            created_at=datetime.now(),
            status="AWAITING_PAYMENT",
            total=total,
            items=items,
        )
        self._session.add(order)
        self._session.flush()

        order_id = order.id
        try:
            wake_up_terminal_and_start_payment(order_id=order_id, total=total)
        except httpx.HTTPError:
            order.status = "PAYMENT_FAILED"
        else:
            self._threadpool.submit(
                self._timeout_order_after,
                order_id=order_id,
                timeout=timedelta(seconds=5),
            )

            def poll_for_success(order_id: int) -> None:
                start = time.monotonic()
                while time.monotonic() - start < 5:
                    time.sleep(0.25)
                    response = httpx.get(f"http://localhost:8090/v1/order/{order_id}")
                    if response.json()["status"] != "DONE":
                        continue

                    with MachineSession() as session:
                        vending = Vending(session=session)
                        vending._payment_successful(order_id)
                        session.commit()

                    return

            self._threadpool.submit(poll_for_success, order_id)

        return order

    def get_order(self, order_id: int) -> Order | None:
        self._session.rollback()
        stmt = select(Order).filter(Order.id == order_id)
        return self._session.execute(stmt).scalars().first()

    @staticmethod
    def _timeout_order_after(order_id: int, timeout: timedelta) -> None:
        time.sleep(timeout.total_seconds())
        stmt = (
            select(Order)
            .filter(
                Order.id == order_id,
                Order.status == "AWAITING_PAYMENT",
            )
            .with_for_update()
        )

        with MachineSession() as session:
            orders = session.execute(stmt).scalars().all()
            for order in orders:
                order.status = "PAYMENT_TIMEOUT"
            session.commit()

    def _payment_successful(self, order_id: int) -> None:
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
                    serial = Serial("/dev/ttyUSB0", timeout=1)
                    serial.open()
                    engine_controller_address = 0x02
                    drive_command = 0x13
                    engine_no = engine_row * 10 + engine_column
                    steps = 0x1
                    frame = [engine_controller_address, drive_command, engine_no, steps]
                    frame_with_checksum = frame + [sum(frame) & 0xFF]
                    payload = bytes(frame_with_checksum)
                    serial.write(payload)
                    response = serial.read(length=2)
                    if response == ACK:
                        lower_stock_on_engine(engine_row, engine_column)
                    elif response == NACK:
                        raise Exception("Dispensing error")
        except Exception:
            logger.exception("Dispensing error!")
            order.status = "DISPENSING_ERROR"
        else:
            stmt = select(Order).filter(Order.id == order_id).with_for_update()

            order = self._session.execute(stmt).scalars().first()
            order.status = "DONE"

        self._session.commit()


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
