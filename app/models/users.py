from uuid import UUID
from sqlmodel import SQLModel, select

from app.db.database import Session
from app.models.courses import Participation, Course


class User(SQLModel):
    id: UUID
    username: str
    email: str
    full_name: str | None

    def get_joined_courses(self, session: Session) -> list["Course"]:
        statement = (
            select(Course)
            .join(Participation, Participation.course_id == Course.id)
            .where(Participation.student_id == self.id)
        )
        results = session.exec(statement)
        return results.all()
