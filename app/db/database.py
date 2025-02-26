from fastapi import Depends
from typing import Annotated

from sqlmodel import Session, create_engine

from app.core.config import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=20,  # Increase the base pool size
    max_overflow=40,  # Allow extra connections if needed
    pool_timeout=30,  # Time to wait before raising TimeoutError
)


# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
