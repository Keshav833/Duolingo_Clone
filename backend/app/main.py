from fastapi import FastAPI

from .database import Base, engine
from . import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Duolingo Clone API is running"}