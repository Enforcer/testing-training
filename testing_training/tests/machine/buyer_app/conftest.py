import os
from pathlib import Path

import pytest
import uvicorn
from multiprocessing import Process

from sqlalchemy import create_engine

from testing_training.machine.database import Base, Session


@pytest.fixture(autouse=True)
def clean_db() -> None:
    sqlite_file = Path(__file__).parent / "test_db.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")
    os.environ["DB_ENGINE_URL"] = f"sqlite:///{sqlite_file}"
    Session.remove()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)


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
