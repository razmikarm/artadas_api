from datetime import time
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, model_validator


# Import only for type checking
# Avoids forward references
if TYPE_CHECKING:
    from app.models.trainings import Training


class TimeRange(SQLModel):
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time", mode="before")
    def truncate_seconds(cls, value):
        if isinstance(value, str):
            try:
                value = time.fromisoformat(value)
            except ValueError:
                raise ValueError("Invalid time format. Use HH:MM")
            if value.minute % 5 != 0:
                raise ValueError("Time must be in 5-minute intervals")
            return value.strftime("%H:%M")
        elif isinstance(value, time):
            # Convert time object to string
            return value.strftime("%H:%M")

    @model_validator(mode="after")
    def validate_time_range(self) -> dict:
        start_time_obj = time.fromisoformat(self.start_time)
        end_time_obj = time.fromisoformat(self.end_time)
        if start_time_obj >= end_time_obj:
            raise ValueError("'start_time' must be earlier than 'end_time'")

        return self


class SchedulerCreate(SQLModel):
    monday: TimeRange | None = None
    tuesday: TimeRange | None = None
    wednesday: TimeRange | None = None
    thursday: TimeRange | None = None
    friday: TimeRange | None = None
    saturday: TimeRange | None = None
    sunday: TimeRange | None = None


class Scheduler(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    training_id: UUID = Field(foreign_key="training.id", unique=True)

    monday: dict | None = Field(default=None, sa_column=Column(JSON))
    tuesday: dict | None = Field(default=None, sa_column=Column(JSON))
    wednesday: dict | None = Field(default=None, sa_column=Column(JSON))
    thursday: dict | None = Field(default=None, sa_column=Column(JSON))
    friday: dict | None = Field(default=None, sa_column=Column(JSON))
    saturday: dict | None = Field(default=None, sa_column=Column(JSON))
    sunday: dict | None = Field(default=None, sa_column=Column(JSON))

    training: "Training" = Relationship(back_populates="scheduler")
