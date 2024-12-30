from uuid import UUID
from datetime import datetime, UTC


from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlalchemy import func
from app.db.database import DBSession
from app.models.users import User
from app.models.topics import TopicReadList, Topic, Syllabus
from app.models.courses import CourseCreate, Course, CourseReadSingle, CourseUpdate, CourseReadList

router = APIRouter(prefix="/courses")


@router.get("/", response_model=list[CourseReadList])
def list_courses(session: DBSession, offset: int = 0, limit: int = 100) -> list[CourseReadList]:
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    return courses


@router.post("/", response_model=CourseReadSingle, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, session: DBSession) -> CourseReadSingle:
    # Check if user exists
    user = session.get(User, course.creator_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_course = Course.model_validate(course)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course


@router.get("/{course_id}", response_model=CourseReadSingle)
def read_course(course_id: UUID, session: DBSession) -> CourseReadSingle:
    course = session.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("/{course_id}/topics", response_model=list[TopicReadList])
def read_course_topics(course_id: UUID, session: DBSession) -> list[TopicReadList]:
    course = session.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course.topics


@router.put("/{course_id}/topics/{topic_id}", response_model=CourseReadSingle)
def add_topic_to_course(course_id: UUID, topic_id: UUID, session: DBSession) -> list[TopicReadList]:
    course = session.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    topic_count = session.exec(select(func.count()).where(Syllabus.course_id == course_id)).one()
    syllabus = Syllabus(course_id=course_id, topic_id=topic_id, sequence=topic_count + 1)
    session.add(syllabus)
    session.commit()
    return course


@router.patch("/{course_id}", response_model=CourseReadSingle)
def update_course(course_id: UUID, course_update: CourseUpdate, session: DBSession) -> CourseReadSingle:
    db_course = session.get(Course, course_id)
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Update only provided fields
    course_data = course_update.model_dump(exclude_unset=True)
    for key, value in course_data.items():
        setattr(db_course, key, value)

    db_course.last_updated_at = datetime.now(UTC)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course
