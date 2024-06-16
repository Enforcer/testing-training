from unittest.mock import Mock

import httpx
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from testing_training.terminal.app import app


def test_healthcheck() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


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
                    "timeout": 60,
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
                    "timeout": 60,
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ACCEPTED"}
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Failed to send notification for order 321"
