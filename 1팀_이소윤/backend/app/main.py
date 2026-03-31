from fastapi import FastAPI

from . import models
from .database import Base, engine, ensure_movies_autoincrement
from .routers import movies, reviews

app = FastAPI(title="Movie Review Sentiment API")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_movies_autoincrement()


app.include_router(movies.router)
app.include_router(reviews.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
