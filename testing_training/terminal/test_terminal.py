import pytest
from unittest.mock import Mock

import httpx
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from testing_training.terminal.app import app


@pytest.fixture(autouse=True)
def clean_fail_mode() -> None:
    with TestClient(app) as client:
        response = client.post("/_fail_mode?fail_mode=false")
        response.raise_for_status()
        yield
        response = client.post("/_fail_mode?fail_mode=false")
        response.raise_for_status()


def test_healthcheck() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_healthcheck_500_if_in_fail_mode() -> None:
    with TestClient(app) as client:
        response = client.post("/_fail_mode?fail_mode=true")
        response.raise_for_status()

        response = client.get("/v1/healthcheck")
        assert response.status_code == 500
        assert response.json() == {"status": "INTERNAL_SERVER_ERROR"}

        response = client.post("/_fail_mode?fail_mode=false")
        response.raise_for_status()

        response = client.get("/v1/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_responds_500_on_order_if_in_fail_mode() -> None:
    with TestClient(app) as client:
        response = client.post("/_fail_mode?fail_mode=true")
        response.raise_for_status()

        response = client.post(
            "/v1/order",
            json={
                "order": {
                    "id": "123",
                    "price": {
                        "currency": "PLN",
                        "amount": "10000",
                    },
                    "description": "test",
                },
                "technical_info": {
                    "notification_url": "http://callback_hostname/v1/terminal_notifications",
                },
            },
        )

        assert response.status_code == 500
        assert response.json() == {"status": "INTERNAL_SERVER_ERROR"}


def test_sends_notification_for_successful_order_for_given_url(
    monkeypatch: MonkeyPatch,
) -> None:
    mock = Mock(return_value=httpx.Response(200))
    monkeypatch.setattr(httpx, "post", mock)

    with TestClient(app) as client:
        response = client.post(
            "/v1/order",
            json={
                "order": {
                    "id": "123",
                    "price": {
                        "currency": "PLN",
                        "amount": "10000",
                    },
                    "description": "test",
                },
                "technical_info": {
                    "notification_url": "http://callback_hostname/v1/terminal_notifications",
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ACCEPTED"}


def test_logs_problem_if_request_with_notification_failed(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    mock = Mock(return_value=httpx.Response(500))
    monkeypatch.setattr(httpx, "post", mock)

    with TestClient(app) as client:
        response = client.post(
            "/v1/order",
            json={
                "order": {
                    "id": "321",
                    "price": {
                        "currency": "PLN",
                        "amount": "10000",
                    },
                    "description": "test",
                },
                "technical_info": {
                    "notification_url": "http://callback_hostname/v1/terminal_notifications",
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ACCEPTED"}
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Failed to send notification for order 321"
