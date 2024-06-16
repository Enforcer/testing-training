from pydantic_settings import BaseSettings


class MachineSettings(BaseSettings):
    SHELVES: int = 6
    ENGINES: int = 6
