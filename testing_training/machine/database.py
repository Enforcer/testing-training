from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session


class Base(DeclarativeBase):
    pass


DATABASE_PATH = Path(__file__).parent / "machine.db"


engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Session = scoped_session(sessionmaker(bind=engine))
