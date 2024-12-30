from typing import TYPE_CHECKING

from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.courses import Course
    from app.models.topics import Topic


class UserBase(SQLModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)

    topics: list["Topic"] = Relationship(back_populates="creator")
    courses: list["Course"] = Relationship(back_populates="creator")
