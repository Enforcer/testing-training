import pytest
import uvicorn
from multiprocessing import Process


@pytest.fixture(scope="session", autouse=True)
def terminal_app() -> None:
    process = Process(
        target=uvicorn.run,
        args=("testing_training.terminal.app:app",),
        kwargs={"port": 8090},
        daemon=True,
    )
    process.start()
    yield
    process.terminate()
    process.join(timeout=3)
