import logging
import asyncio
from typing import Literal

import httpx
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI()

_FAIL_MODE = False
_SUCCESSFUL_ORDER_IDS = set()
_FAIL_ORDER_IDS = set()


class Price(BaseModel):
    currency: Literal["PLN"]
    amount: int


class Order(BaseModel):
    id: str
    price: Price
    description: str


class TechnicalInfo(BaseModel):
    notification_url: HttpUrl


class Payload(BaseModel):
    order: Order
    technical_info: TechnicalInfo


async def send_notification(order_id: str, url: str) -> None:
    await asyncio.sleep(1)
    _SUCCESSFUL_ORDER_IDS.add(order_id)
    # response = httpx.post(url, json={"order_id": order_id, "status": "DONE"})
    # if response.status_code != 200:
    #     logging.error(f"Failed to send notification for order {order_id}")


@app.post("/v1/order")
async def order(payload: Payload, background_tasks: BackgroundTasks) -> JSONResponse:
    if _FAIL_MODE:
        _FAIL_ORDER_IDS.add(payload.order.id)
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )

    url = str(payload.technical_info.notification_url)
    background_tasks.add_task(send_notification, payload.order.id, url)
    return JSONResponse(content={"status": "ACCEPTED"})


@app.get("/v1/order/{order_id}")
async def order_status(order_id: str) -> JSONResponse:
    if _FAIL_MODE:
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )

    if order_id in _SUCCESSFUL_ORDER_IDS:
        return JSONResponse(content={"order_id": order_id, "status": "DONE"})
    elif order_id in _FAIL_ORDER_IDS:
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )
    else:
        return JSONResponse(content={"status": "ACCEPTED", "order_id": order_id})


@app.get("/v1/healthcheck")
async def healthcheck() -> JSONResponse:
    if _FAIL_MODE:
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )
    return JSONResponse(content={"status": "ok"})


@app.post("/_fail_mode")
def set_fail_mode() -> JSONResponse:
    globals()["_FAIL_MODE"] = True
    return JSONResponse(content={"status": "ok", "fail_mode": _FAIL_MODE})


@app.delete("/_fail_mode")
def reset_fail_mode() -> JSONResponse:
    globals()["_FAIL_MODE"] = False
    return JSONResponse(content={"status": "ok", "fail_mode": _FAIL_MODE})
