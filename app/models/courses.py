from typing import Annotated, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, UTC

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship, func
from app.models.topics import Syllabus


# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.topics import Topic

PositiveInt = Annotated[int, Field(gt=-1)]


class CourseBase(SQLModel):
    """Base Course model with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    price: PositiveInt
    description: str


class Course(CourseBase, table=True):
    """Database model for Courses."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    creator_id: UUID = Field()  # foreign_key="user.id"
    tg_group_id: str | None = None
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

    topics: list["Topic"] = Relationship(
        back_populates="courses", link_model=Syllabus, sa_relationship_kwargs={"order_by": "Syllabus.sequence"}
    )


class CourseCreate(CourseBase):
    """Model for creating new Courses."""

    model_config = ConfigDict(extra="forbid")


class CourseReadList(CourseBase):
    """Model for reading multiple Course data."""

    id: UUID
    creator_id: UUID


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
