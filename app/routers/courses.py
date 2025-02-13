from uuid import UUID
from datetime import datetime, UTC

from scheduler.tasks import create_group_topic
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db.database import DBSession
from app.models.topics import TopicReadList, Topic, Syllabus
from app.models.courses import CourseCreate, Course, CourseReadSingle, CourseUpdate, CourseReadList, CourseParticipation

from app.utils.auth import CurrentUser

router = APIRouter(prefix="/courses")


@router.get("/", response_model=list[CourseReadList])
def list_courses(session: DBSession, page: int = 1, page_size: int = 10) -> list[CourseReadList]:
    courses = session.exec(select(Course).offset((page - 1) * page_size).limit(page_size)).all()
    return courses


@router.post("/", response_model=CourseReadSingle, status_code=status.HTTP_201_CREATED)
def create_course(user: CurrentUser, course: CourseCreate, session: DBSession) -> CourseReadSingle:
    db_course = Course.model_validate(course, update={"creator_id": user.id})
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    if db_course.price == 0:
        create_group_topic.delay(db_course.name, user.username)
    return db_course


@router.get("/joined", response_model=list[CourseReadList])
def read_courses_user_joined(user: CurrentUser, session: DBSession) -> list[CourseReadList]:
    return user.get_joined_courses(session)


@router.get("/by/me", response_model=list[CourseReadList])
def read_courses_current_user_created(user: CurrentUser, session: DBSession) -> list[CourseReadList]:
    my_courses = session.exec(select(Course).where(Course.creator_id == user.id)).all()
    return my_courses


@router.get("/by/{user_id}", response_model=list[CourseReadList])
def read_courses_given_user_created(user_id: UUID, session: DBSession) -> list[CourseReadList]:
    user_courses = session.exec(select(Course).where(Course.creator_id == user_id)).all()
    return user_courses


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


@router.post("/{course_id}/topics/{topic_id}", response_model=list[TopicReadList])
def add_topic_to_course(user: CurrentUser, course_id: UUID, topic_id: UUID, session: DBSession) -> list[TopicReadList]:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    topic = session.exec(select(Topic).where((Topic.id == topic_id) & (Topic.creator_id == user.id))).one_or_none()
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    syllabus_record = session.exec(
        select(Syllabus).where((Syllabus.topic_id == topic_id) & (Syllabus.course_id == course_id))
    ).one_or_none()
    if syllabus_record is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Topic already exists in the course")

    topic_count = Syllabus.get_topic_count(course_id, session)
    syllabus = Syllabus(course_id=course_id, topic_id=topic_id, sequence=topic_count + 1)
    session.add(syllabus)
    session.commit()
    return course.topics


@router.delete("/{course_id}/topics/{topic_id}", response_model=list[TopicReadList])
def delete_topic_from_course(
    user: CurrentUser, course_id: UUID, topic_id: UUID, session: DBSession
) -> list[TopicReadList]:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    syllabus_record = session.exec(
        select(Syllabus).where((Syllabus.topic_id == topic_id) & (Syllabus.course_id == course_id))
    ).one_or_none()
    if syllabus_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found in the course")
    topic_count = Syllabus.get_topic_count(course_id, session)
    Syllabus.change_topic_position(course_id, topic_id, topic_count, session)
    session.delete(syllabus_record)
    session.commit()
    return course.topics


@router.post("/{course_id}/topics/{topic_id}/{position}", response_model=list[TopicReadList])
def change_topic_position_in_course(
    user: CurrentUser, course_id: UUID, topic_id: UUID, position: int, session: DBSession
) -> list[TopicReadList]:
    if position < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Non-positive position is not allowed")
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    syllabus_record = session.exec(
        select(Syllabus).where((Syllabus.topic_id == topic_id) & (Syllabus.course_id == course_id))
    ).one_or_none()
    if syllabus_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found in the course")

    topic_count = Syllabus.get_topic_count(course_id, session)
    if position > topic_count:
        position = topic_count
    Syllabus.change_topic_position(course_id, topic_id, position, session)
    return course.topics


@router.get("/{course_id}/students", response_model=list[UUID])
def read_course_students_ids(user: CurrentUser, course_id: UUID, session: DBSession) -> list[UUID]:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course.get_students_ids(session)


@router.post("/{course_id}/join", response_model=CourseReadSingle)
def join_the_course(user: CurrentUser, course_id: UUID, session: DBSession) -> CourseReadSingle:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id != user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    c_participation = CourseParticipation(course_id=course_id, student_id=user.id)
    session.add(c_participation)
    session.commit()
    return course


@router.post("/{course_id}/leave", response_model=dict)
def leave_the_course(user: CurrentUser, course_id: UUID, session: DBSession) -> dict:
    c_participation = session.exec(
        select(CourseParticipation).where(
            (CourseParticipation.course_id == course_id) & (CourseParticipation.student_id == user.id)
        )
    ).one_or_none()
    if c_participation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    session.delete(c_participation)
    session.commit()
    return {"messagge": "Successfully left the course"}


@router.patch("/{course_id}", response_model=CourseReadSingle)
def update_course(
    user: CurrentUser, course_id: UUID, course_update: CourseUpdate, session: DBSession
) -> CourseReadSingle:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Update only provided fields
    course_data = course_update.model_dump(exclude_unset=True)
    for key, value in course_data.items():
        setattr(course, key, value)

    course.updated_at = datetime.now(UTC).replace(tzinfo=None)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}", response_model=dict)
def delete_course(user: CurrentUser, course_id: UUID, session: DBSession) -> dict:
    course = session.exec(select(Course).where((Course.id == course_id) & (Course.creator_id == user.id))).one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Delete the Course
    session.delete(course)
    session.commit()
    return {"message": "Course has been deleted"}
