import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, Response, status

from . import database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("taskforge-worker")


async def worker_loop() -> None:
    interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))
    batch_size = int(os.getenv("WORKER_BATCH_SIZE", "5"))

    while True:
        try:
            processed_count = await asyncio.to_thread(database.process_tasks, batch_size)
            if processed_count:
                logger.info("Processed %s TaskForge task(s)", processed_count)
        except Exception:
            logger.exception("Worker polling cycle failed")

        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    worker_task = asyncio.create_task(worker_loop())
    logger.info("TaskForge worker loop started")

    try:
        yield
    finally:
        worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await worker_task


app = FastAPI(title="TaskForge Worker Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "alive", "service": "worker"}


@app.get("/ready")
def ready(response: Response) -> dict[str, Any]:
    try:
        database.database_ready()
        return {"status": "ready", "database": "reachable"}
    except Exception as exc:
        logger.exception("Worker readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database": "unreachable", "error": str(exc)}
