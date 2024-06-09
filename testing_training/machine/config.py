from pathlib import Path

from pydantic_settings import BaseSettings


STATIC_FILES_DIR: Path = Path(__file__).parent.parent / "images"


class MachineSettings(BaseSettings):
    SHELVES: int = 6
    ENGINES: int = 6
