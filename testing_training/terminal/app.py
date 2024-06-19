import logging
import asyncio
from typing import Literal

import httpx
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI()

_FAIL_MODE = False


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
    response = httpx.post(url, json={"order_id": order_id, "status": "DONE"})
    if response.status_code != 200:
        logging.error(f"Failed to send notification for order {order_id}")


@app.post("/v1/order")
async def order(payload: Payload, background_tasks: BackgroundTasks) -> JSONResponse:
    if _FAIL_MODE:
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )

    url = str(payload.technical_info.notification_url)
    background_tasks.add_task(send_notification, payload.order.id, url)
    return JSONResponse(content={"status": "ACCEPTED"})


@app.get("/v1/healthcheck")
async def healthcheck() -> JSONResponse:
    if _FAIL_MODE:
        return JSONResponse(
            content={"status": "INTERNAL_SERVER_ERROR"}, status_code=500
        )
    return JSONResponse(content={"status": "ok"})


@app.post("/_fail_mode")
async def set_fail_mode(fail_mode: bool) -> JSONResponse:
    global _FAIL_MODE
    _FAIL_MODE = fail_mode
    return JSONResponse(content={"status": "ok"})
