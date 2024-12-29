from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.db.database import DBSession
from app.models.users import User, UserCreate, UserRead
from app.models.courses import CourseReadList

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def read_users(session: DBSession):
    statement = select(User)
    users = session.exec(statement).all()
    return users


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: DBSession):
    db_user = User.model_validate(user)  # Convert UserCreate to User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: UUID, session: DBSession):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/courses", response_model=list[CourseReadList])
def read_user_courses(user_id: UUID, session: DBSession):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.courses
