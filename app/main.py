import logging
import multiprocessing
from fastapi import FastAPI
from aiogram.types import Update
from contextlib import asynccontextmanager
from app.utils.middleware import LoggingMiddleware

from app.utils.migrations import apply_migrations
from app.routers import courses, topics, trainings
from app.core.config import settings
from tg_bot.bot import bot, dp

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

app.include_router(topics.router, prefix="/api", tags=["Topics"])
app.include_router(courses.router, prefix="/api", tags=["Courses"])
app.include_router(trainings.router, prefix="/api", tags=["Trainings"])


@app.post("/webhook")
async def telegram_webhook(update: dict):
    try:
        telegram_update = Update.model_validate(update)
        await dp.feed_update(bot, telegram_update)
    except Exception as e:
        # Log the error
        print(f"Error processing update: {e}")
    return {"status": "ok"}


if settings.debug:
    app.add_middleware(LoggingMiddleware)
