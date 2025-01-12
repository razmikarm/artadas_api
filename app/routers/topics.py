from uuid import UUID
from datetime import datetime, UTC


from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db.database import DBSession
from app.models.topics import TopicCreate, Topic, TopicReadSingle, TopicUpdate, TopicReadList
from app.utils.auth import CurrentUser

router = APIRouter(prefix="/topics")


@router.get("/", response_model=list[TopicReadList])
def list_topics(session: DBSession, offset: int = 0, limit: int = 100) -> list[TopicReadList]:
    topics = session.exec(select(Topic).offset(offset).limit(limit)).all()
    return topics


@router.post("/", response_model=TopicReadSingle, status_code=status.HTTP_201_CREATED)
def create_topic(user: CurrentUser, topic: TopicCreate, session: DBSession) -> TopicReadSingle:
    db_topic = Topic.model_validate(topic, update={"creator_id": user.id})
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic


@router.get("/by/me", response_model=list[TopicReadList])
def read_current_user_topics(user: CurrentUser, session: DBSession):
    user_courses = session.exec(select(Topic).where(Topic.creator_id == user.id)).all()
    return user_courses


# @router.get("/by/{user_id}", response_model=list[TopicReadList])
# def read_given_user_topics(user_id: UUID, session: DBSession):
#     user_courses = session.exec(select(Topic).where(Topic.creator_id == user_id)).all()
#     return user_courses


@router.get("/{topic_id}", response_model=TopicReadSingle)
def read_topic(topic_id: UUID, session: DBSession) -> TopicReadSingle:
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return topic


@router.patch("/{topic_id}", response_model=TopicReadSingle)
def update_topic(user: CurrentUser, topic_id: UUID, topic_update: TopicUpdate, session: DBSession) -> TopicReadSingle:
    topic = session.exec(select(Topic).where((Topic.id == topic_id) & (Topic.creator_id == user.id))).one_or_none()
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Update only provided fields
    topic_data = topic_update.model_dump(exclude_unset=True)
    for key, value in topic_data.items():
        setattr(topic, key, value)

    topic.updated_at = datetime.now(UTC).replace(tzinfo=None)
    session.add(topic)
    session.commit()
    session.refresh(topic)
    return topic


@router.delete("/{topic_id}", response_model=dict)
def delete_topic(user: CurrentUser, topic_id: UUID, session: DBSession) -> dict:
    topic = session.exec(select(Topic).where((Topic.id == topic_id) & (Topic.creator_id == user.id))).one_or_none()
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Delete the Topic
    session.delete(topic)
    session.commit()
    return {"message": "Topic has been deleted"}
