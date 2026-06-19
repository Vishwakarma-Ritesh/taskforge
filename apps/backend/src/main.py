import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from . import database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("taskforge-backend")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        database.initialize_schema()
        logger.info("TaskForge database schema is ready")
    except Exception:
        logger.exception("Schema initialization failed; readiness will remain unhealthy")

    yield


app = FastAPI(title="TaskForge Backend API", version="1.0.0", lifespan=lifespan)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class Task(BaseModel):
    id: int
    title: str
    description: str | None
    processed: bool
    created_at: datetime
    processed_at: datetime | None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "alive", "service": "backend"}


@app.get("/ready")
def ready(response: Response) -> dict[str, Any]:
    try:
        database.database_ready()
        return {"status": "ready", "database": "reachable"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database": "unreachable", "error": str(exc)}


@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[dict[str, Any]]:
    try:
        return database.list_tasks()
    except Exception as exc:
        logger.exception("Could not list tasks")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def post_task(payload: TaskCreate) -> dict[str, Any]:
    try:
        return database.create_task(payload.title, payload.description)
    except Exception as exc:
        logger.exception("Could not create task")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.get("/items", response_model=list[Task])
def get_items() -> list[dict[str, Any]]:
    return get_tasks()


@app.post("/items", response_model=Task, status_code=status.HTTP_201_CREATED)
def post_item(payload: TaskCreate) -> dict[str, Any]:
    return post_task(payload)

