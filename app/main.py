from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.migrations import apply_migrations
from app.routers import users, courses, topics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup logic here
    apply_migrations()  # Apply migrations when the app starts
    yield  # Control returns to the application during runtime
    # Perform any shutdown logic here if needed


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, tags=["Users"])
app.include_router(courses.router, tags=["Courses"])
app.include_router(topics.router, tags=["Topics"])
