from typing import Annotated, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, UTC

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship, func


# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.courses import Course
    from app.models.users import User

PositiveInt = Annotated[int, Field(gt=-1)]


class Syllabus(SQLModel, table=True):
    course_id: UUID = Field(foreign_key="course.id", primary_key=True)
    topic_id: UUID = Field(foreign_key="topic.id", primary_key=True)
    sequence: PositiveInt


class TopicBase(SQLModel):
    """Base Topic model with common fields."""

    model_config = ConfigDict(from_attributes=True)

    title: str
    content: str
    creator_id: UUID


class Topic(TopicBase, table=True):
    """Database model for Topics."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    creator_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )
    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )

    creator: "User" = Relationship(back_populates="topics")
    courses: list["Course"] = Relationship(back_populates="topics", link_model=Syllabus)


class TopicCreate(TopicBase):
    """Model for creating new Topics."""

    model_config = ConfigDict(extra="forbid")


class TopicReadList(TopicBase):
    """Model for reading multiple Topic data."""

    id: UUID


class TopicReadSingle(TopicReadList):
    """Model for reading single Topic data."""

    last_updated_at: datetime
    created_at: datetime


class TopicUpdate(SQLModel):
    """Model for updating Topic data."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    content: str | None = None
