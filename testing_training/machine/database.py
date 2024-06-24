import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session


class Base(DeclarativeBase):
    pass


DATABASE_PATH = Path(__file__).parent / "machine.db"

engine_url = os.environ.get("DB_ENGINE_URL") or f"sqlite:///{DATABASE_PATH}"
engine = create_engine(engine_url)
Session = scoped_session(sessionmaker(bind=engine))
