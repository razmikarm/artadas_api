from uuid import UUID
from datetime import datetime, UTC


from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.db.database import DBSession
from app.models.topics import TopicCreate, Topic, TopicReadSingle, TopicUpdate, TopicReadList

router = APIRouter()


@router.get("/", response_model=list[TopicReadList])
def list_topics(session: DBSession, offset: int = 0, limit: int = 100) -> list[TopicReadList]:
    topics = session.exec(select(Topic).offset(offset).limit(limit)).all()
    return topics


@router.post("/", response_model=TopicReadSingle, status_code=status.HTTP_201_CREATED)
def create_topic(topic: TopicCreate, session: DBSession) -> TopicReadSingle:
    db_topic = Topic.model_validate(topic)
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic


@router.get("/{topic_id}", response_model=TopicReadSingle)
def read_topic(topic_id: UUID, session: DBSession) -> TopicReadSingle:
    match session.get(Topic, topic_id):
        case None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        case topic:
            return topic


@router.patch("/{topic_id}", response_model=TopicReadSingle)
def update_topic(topic_id: UUID, topic_update: TopicUpdate, session: DBSession) -> TopicReadSingle:
    db_topic = session.get(Topic, topic_id)

    match db_topic:
        case None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        case topic:
            # Update only provided fields
            topic_data = topic_update.model_dump(exclude_unset=True)
            for key, value in topic_data.items():
                setattr(db_topic, key, value)

            db_topic.last_updated_at = datetime.now(UTC)
            session.add(db_topic)
            session.commit()
            session.refresh(db_topic)
            return db_topic
