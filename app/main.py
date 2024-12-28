from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routers import users, courses, topics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup logic here
    init_db()  # Initialize the database
    yield  # Control returns to the application during runtime
    # Perform any shutdown logic here if needed


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(topics.router, prefix="/topics", tags=["Topics"])
