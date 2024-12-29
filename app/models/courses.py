from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime, UTC

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship, func
from app.models.topics import Syllabus


PositiveInt = Annotated[int, Field(gt=-1)]


class CourseBase(SQLModel):
    """Base Course model with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    price: PositiveInt
    description: str
    creator_id: UUID


class Course(CourseBase, table=True):
    """Database model for Courses."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    tg_group_id: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )
    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )

    creator_id: UUID = Field(foreign_key="user.id")
    creator: "User" = Relationship(back_populates="courses")
    topics: list["Topic"] = Relationship(back_populates="courses", link_model=Syllabus)


class CourseCreate(CourseBase):
    """Model for creating new Courses."""

    model_config = ConfigDict(extra="forbid")


class CourseReadList(CourseBase):
    """Model for reading multiple Course data."""

    id: UUID


class CourseReadSingle(CourseReadList):
    """Model for reading single Course data."""

    tg_group_id: str | None
    last_updated_at: datetime
    created_at: datetime


class CourseUpdate(SQLModel):
    """Model for updating Course data."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    price: PositiveInt | None = None
    description: str | None = None
    tg_group_id: str | None = None
