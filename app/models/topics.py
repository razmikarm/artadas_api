from typing import Annotated, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, UTC
from operator import add, sub
from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship, func, select, update

from app.db.database import Session

# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.courses import Course

PositiveInt = Annotated[int, Field(gt=-1)]


class Syllabus(SQLModel, table=True):
    course_id: UUID = Field(foreign_key="course.id", primary_key=True)
    topic_id: UUID = Field(foreign_key="topic.id", primary_key=True)
    sequence: PositiveInt

    @classmethod
    def change_topic_position(cls, course_id: UUID, topic_id: UUID, new_pos: int, session: Session):
        syllabus = session.exec(
            select(cls).where((cls.topic_id == topic_id) & (cls.course_id == course_id))
        ).one_or_none()
        curr_pos = syllabus.sequence
        if new_pos > curr_pos:
            op = sub
            lower_pos, upper_pos = curr_pos + 1, new_pos
        elif new_pos < curr_pos:
            op = add
            lower_pos, upper_pos = new_pos, curr_pos - 1
        else:
            return

        stmt = (
            update(cls)
            .where((cls.course_id == course_id) & (cls.sequence.between(lower_pos, upper_pos)))
            .values(sequence=op(cls.sequence, 1))
        )
        session.exec(stmt)
        syllabus.sequence = new_pos
        session.commit()

    @classmethod
    def get_topic_count(cls, course_id: UUID, session: Session) -> int:
        return session.exec(select(func.count()).where(cls.course_id == course_id)).one_or_none()


class TopicBase(SQLModel):
    """Base Topic model with common fields."""

    model_config = ConfigDict(from_attributes=True)

    title: str
    content: str


class Topic(TopicBase, table=True):
    """Database model for Topics."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    creator_id: UUID = Field()  # foreign_key="user.id"
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

    courses: list["Course"] = Relationship(back_populates="topics", link_model=Syllabus)


class TopicCreate(TopicBase):
    """Model for creating new Topics."""

    model_config = ConfigDict(extra="forbid")


class TopicReadList(TopicBase):
    """Model for reading multiple Topic data."""

    id: UUID
    creator_id: UUID


class TopicReadSingle(TopicReadList):
    """Model for reading single Topic data."""

    updated_at: datetime
    created_at: datetime


class TopicUpdate(SQLModel):
    """Model for updating Topic data."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    content: str | None = None
