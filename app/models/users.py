from uuid import UUID
from sqlmodel import SQLModel, select

from app.db.database import Session
from app.models.courses import CourseParticipation, Course


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
