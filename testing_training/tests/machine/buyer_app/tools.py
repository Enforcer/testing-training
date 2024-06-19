import httpx

from testing_training.myserial import Serial


def simulate_engine_timeout() -> None:
    Serial._TIMEOUT = True
    Serial._SIMULATE_ERROR = False


def simulate_engine_error() -> None:
    Serial._SIMULATE_ERROR = True
    Serial._TIMEOUT = False


def restore_engine_state() -> None:
    Serial._TIMEOUT = False
    Serial._SIMULATE_ERROR = False


def simulate_terminal_malfunction() -> None:
    response = httpx.post("http://localhost:8090/_fail_mode")
    response.raise_for_status()


def restore_terminal() -> None:
    response = httpx.delete("http://localhost:8090/_fail_mode")
    response.raise_for_status()
