from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from testing_training.machine.products import list_products
from testing_training.machine.buyer_app.order import Order


class Vending:
    def __init__(self, session: Session) -> None:
        self._session = session

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
        return order

    def get_order(self, order_id: int) -> Order | None:
        stmt = select(Order).filter(Order.id == order_id)
        return self._session.execute(stmt).scalars().first()

    def timeout_orders(self, timeout: timedelta) -> None:
        stmt = select(Order).filter(
            Order.status == "AWAITING_PAYMENT",
            Order.created_at < datetime.now() - timeout,
        ).with_for_update()

        orders = self._session.execute(stmt).scalars().all()
        for order in orders:
            order.status = "PAYMENT_TIMEOUT"

    def payment_successful(self, order_id: int) -> None:
        stmt = select(Order).filter(
            Order.id == order_id,
        ).with_for_update()

        order = self._session.execute(stmt).scalars().first()
        order.status = "DISPENSING"
