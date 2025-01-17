from uuid import UUID, uuid4
from pydantic import ConfigDict
from datetime import datetime, UTC
from typing import Annotated, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, func, select

from app.db.database import Session
from app.models.topics import Syllabus


# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.topics import Topic
    # from app.models.trainings import Training

PositiveInt = Annotated[int, Field(gt=-1)]


class CourseParticipation(SQLModel, table=True):
    __tablename__ = "course_participation"

    course_id: UUID = Field(foreign_key="course.id", primary_key=True)
    student_id: UUID = Field(primary_key=True)

    # courses: list["Course"] = Relationship(
    #     back_populates="participations"
    # )


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
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )

    # training: "Training" | None = Relationship(back_populates="course")
    topics: list["Topic"] = Relationship(
        back_populates="courses", link_model=Syllabus, sa_relationship_kwargs={"order_by": "Syllabus.sequence"}
    )

    # participations: list["CourseParticipation"] = Relationship(
    #     back_populates="courses", link_model=CourseParticipation, sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    # )

    def get_students_ids(self, session: Session) -> list[UUID]:
        statement = select(CourseParticipation.student_id).where(CourseParticipation.course_id == self.id)
        results = session.exec(statement)
        return results.all()


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
    updated_at: datetime
    created_at: datetime


class CourseUpdate(SQLModel):
    """Model for updating Course data."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    price: PositiveInt | None = None
    description: str | None = None
    tg_group_id: str | None = None
