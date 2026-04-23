from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.database import init_db
from .routers.students import router as students_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="FastAPI Student Management", lifespan=lifespan)


@app.get("/")
def health_check():
    return {"status": "ok"}


app.include_router(students_router)
