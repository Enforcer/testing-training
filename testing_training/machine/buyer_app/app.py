import time
import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Iterator
from threading import Thread, Event

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from testing_training.machine.buyer_app.order import Order
from testing_training.machine.buyer_app.vending import Vending
from testing_training.machine.database import Session
from testing_training.machine.inventory import get_inventory
from testing_training.machine.products import list_products


threadpool = ThreadPoolExecutor(max_workers=4)


@asynccontextmanager
async def lifespan(_: FastAPI) -> Iterator[None]:
    def _timeout_payments(event: Event) -> None:
        TIMEOUT = timedelta(seconds=5)

        while True:
            if event.is_set():
                break

            time.sleep(1)
            with Session() as session:
                vending = Vending(session=session, threadpool=threadpool)
                vending.timeout_orders(timeout=TIMEOUT)
                session.commit()

    stop_event = Event()
    thread = Thread(target=_timeout_payments, args=(stop_event,), daemon=True)
    thread.start()
    yield
    stop_event.set()
    threadpool.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)

STATIC_FILES_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={},
    )


@app.get("/products")
def products() -> list[dict]:
    all_products = list_products()
    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": {
                "amount": product.price.amount,
                "currency": product.price.currency.name,
            },
            "image": base64.b64encode(product.image),
        }
        for product in all_products
    ]


@app.get("/inventory")
def inventory() -> dict[int, int]:
    entries = get_inventory()
    return {entry.product_id: entry.quantity for entry in entries}


class OrderPayload(BaseModel):
    items: dict[int, int]


@app.post("/order")
def order(payload: OrderPayload) -> JSONResponse:
    session = Session()
    vending = Vending(session=session, threadpool=threadpool)
    order = vending.place_order(payload.items)
    response = _order_to_dict(order)
    session.commit()
    return JSONResponse(content=response)


@app.get("/order/{order_id}")
def get_order(order_id: str) -> JSONResponse:
    session = Session()
    vending = Vending(session=session, threadpool=threadpool)
    order = vending.get_order(int(order_id))
    if order is None:
        return JSONResponse(content={"error": "Order not found"}, status_code=404)
    response = _order_to_dict(order)
    return JSONResponse(content=response)


class PaymentNotification(BaseModel):
    order_id: int
    status: str


@app.post("/payment/notifications")
def handle_payment_notification(payload: PaymentNotification) -> JSONResponse:
    session = Session()
    vending = Vending(session=session, threadpool=threadpool)
    vending.payment_successful(payload.order_id)
    session.commit()
    return JSONResponse(content={"success": True})


def _order_to_dict(order: Order) -> dict:
    return {
        "order_id": order.id,
        "status": order.status,
        "total": {
            "amount": str(order.total.amount),
            "currency": order.total.currency.name,
        },
    }
