from uuid import UUID, uuid4
from pydantic import ConfigDict
from datetime import datetime, UTC
from typing import Annotated
from sqlmodel import SQLModel, Field, Relationship, func, select

from app.db.database import Session
from app.models.schedulers import Scheduler, SchedulerCreate


# Import only for type checking
# Avoids forward references
# if TYPE_CHECKING:
#     from app.models.courses import Course

PositiveInt = Annotated[int, Field(gt=-1)]


class TrainingParticipation(SQLModel, table=True):
    __tablename__ = "training_participation"

    student_id: UUID = Field(primary_key=True)  # foreign_key="user.id"
    training_id: UUID = Field(foreign_key="training.id", primary_key=True)

    # training: "Training" = Relationship(back_populates="participations")


class TrainingBase(SQLModel):
    """Base Training model with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    price: PositiveInt
    description: str


class Training(TrainingBase, table=True):
    """Database model for Trainings."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    creator_id: UUID = Field()  # foreign_key="user.id"
    # course_id: UUID | None = Field(default=None, foreign_key="course.id", unique=True, nullable=True)
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

    # course: "Course" | None = Relationship(back_populates="training")
    scheduler: "Scheduler" = Relationship(back_populates="training")

    # participations: list["TrainingParticipation"] = Relationship(
    #     back_populates="training", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    # )

    def get_students_ids(self, session: Session) -> list[UUID]:
        statement = select(TrainingParticipation.student_id).where(TrainingParticipation.training_id == self.id)
        results = session.exec(statement)
        return results.all()


class TrainingCreate(TrainingBase):
    """Model for creating new Trainings."""

    model_config = ConfigDict(extra="forbid")


class TrainingReadList(TrainingBase):
    """Model for reading multiple Training data."""

    id: UUID
    creator_id: UUID
    # course_id: UUID | None


class TrainingReadSingle(TrainingReadList):
    """Model for reading single Training data."""

    scheduler: SchedulerCreate | None
    updated_at: datetime
    created_at: datetime


class TrainingUpdate(SQLModel):
    """Model for updating Training data."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    price: PositiveInt | None = None
    description: str | None = None
