from uuid import UUID
from sqlmodel import SQLModel, select

from app.db.database import Session
from app.models.courses import CourseParticipation, Course
from app.models.trainings import TrainingParticipation, Training


class User(SQLModel):
    id: UUID
    username: str
    email: str
    full_name: str | None

    def get_joined_courses(self, session: Session) -> list["Course"]:
        statement = (
            select(Course)
            .join(CourseParticipation, CourseParticipation.course_id == Course.id)
            .where(CourseParticipation.student_id == self.id)
        )
        results = session.exec(statement)
        return results.all()

    def get_joined_trainings(self, session: Session) -> list["Training"]:
        statement = (
            select(Training)
            .join(TrainingParticipation, TrainingParticipation.training_id == Training.id)
            .where(TrainingParticipation.student_id == self.id)
        )
        results = session.exec(statement)
        return results.all()
