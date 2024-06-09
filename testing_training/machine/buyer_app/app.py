from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from testing_training.machine.config import STATIC_FILES_DIR

app = FastAPI()

app.mount("/images", StaticFiles(directory=STATIC_FILES_DIR), name="images")
