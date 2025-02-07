import logging
import multiprocessing
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.middleware import LoggingMiddleware

from app.utils.migrations import apply_migrations
from app.routers import courses, topics, trainings
from app.core.config import settings

log = logging.getLogger("uvicorn")
log.setLevel(logging.DEBUG if settings.debug else logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup logic here
    log.info("Starting up...")
    log.info("Run alembic upgrade head...")
    process = multiprocessing.Process(target=apply_migrations)
    process.start()
    process.join()  # Wait for the process to finish
    log.info("Finished alembic upgrade.")
    yield  # Control returns to the application during runtime
    log.info("Shutting down...")
    # Perform any shutdown logic here if needed


app = FastAPI(lifespan=lifespan, debug=settings.debug, docs_url=None, redoc_url=None)

app.include_router(topics.router, tags=["Topics"])
app.include_router(courses.router, tags=["Courses"])
app.include_router(trainings.router, tags=["Trainings"])

if settings.debug:
    app.add_middleware(LoggingMiddleware)
