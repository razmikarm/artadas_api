from uuid import UUID
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.db.database import DBSession
from app.models.schedulers import Scheduler, SchedulerCreate
from app.utils.auth import CurrentUser
from app.models.trainings import (
    TrainingCreate,
    Training,
    TrainingReadSingle,
    TrainingUpdate,
    TrainingReadList,
    TrainingParticipation,
)

router = APIRouter(prefix="/trainings")


@router.get("/", response_model=list[TrainingReadList])
def list_trainings(session: DBSession, page: int = 1, page_size: int = 10) -> list[TrainingReadList]:
    trainings = session.exec(select(Training).offset((page - 1) * page_size).limit(page_size)).all()
    return trainings


@router.post("/", response_model=TrainingReadSingle, status_code=status.HTTP_201_CREATED)
def create_training(user: CurrentUser, training: TrainingCreate, session: DBSession) -> TrainingReadSingle:
    db_training = Training.model_validate(training, update={"creator_id": user.id})
    session.add(db_training)
    session.commit()
    session.refresh(db_training)
    return db_training


@router.get("/joined", response_model=list[TrainingReadList])
def read_trainings_user_joined(user: CurrentUser, session: DBSession) -> list[TrainingReadList]:
    return user.get_joined_trainings(session)


@router.get("/by/me", response_model=list[TrainingReadList])
def read_trainings_current_user_created(user: CurrentUser, session: DBSession) -> list[TrainingReadList]:
    my_trainings = session.exec(select(Training).where(Training.creator_id == user.id)).all()
    return my_trainings


@router.get("/by/{user_id}", response_model=list[TrainingReadList])
def read_trainings_given_user_created(user_id: UUID, session: DBSession) -> list[TrainingReadList]:
    user_trainings = session.exec(select(Training).where(Training.creator_id == user_id)).all()
    return user_trainings


@router.get("/{training_id}", response_model=TrainingReadSingle)
def read_training(training_id: UUID, session: DBSession) -> TrainingReadSingle:
    training = session.get(Training, training_id)
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")
    return training


@router.get("/{training_id}/students", response_model=list[UUID])
def read_training_students_ids(user: CurrentUser, training_id: UUID, session: DBSession) -> list[UUID]:
    training = session.exec(
        select(Training).where((Training.id == training_id) & (Training.creator_id == user.id))
    ).one_or_none()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")
    return training.get_students_ids(session)


@router.post("/{training_id}/join", response_model=TrainingReadSingle)
def join_the_training(user: CurrentUser, training_id: UUID, session: DBSession) -> TrainingReadSingle:
    training = session.exec(
        select(Training).where((Training.id == training_id) & (Training.creator_id != user.id))
    ).one_or_none()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")

    t_participation = TrainingParticipation(training_id=training_id, student_id=user.id)
    session.add(t_participation)
    session.commit()
    return training


@router.post("/{training_id}/schedule", response_model=TrainingReadSingle, status_code=status.HTTP_201_CREATED)
def scheduler_the_training(
    user: CurrentUser, training_id: UUID, scheduler: SchedulerCreate, session: DBSession
) -> TrainingReadSingle:
    training = session.exec(
        select(Training).where((Training.id == training_id) & (Training.creator_id == user.id))
    ).one_or_none()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")

    if training.scheduler is not None:
        session.delete(training.scheduler)
        session.commit()
    db_scheduler = Scheduler.model_validate(scheduler.model_dump(), update={"training_id": training_id})
    session.add(db_scheduler)
    session.commit()

    return training


@router.post("/{training_id}/leave", response_model=dict)
def leave_the_training(user: CurrentUser, training_id: UUID, session: DBSession) -> dict:
    t_participation = session.exec(
        select(TrainingParticipation).where(
            (TrainingParticipation.training_id == training_id) & (TrainingParticipation.student_id == user.id)
        )
    ).one_or_none()
    if t_participation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")

    session.delete(t_participation)
    session.commit()
    return {"messagge": "Successfully left the training"}


@router.patch("/{training_id}", response_model=TrainingReadSingle)
def update_training(
    user: CurrentUser, training_id: UUID, training_update: TrainingUpdate, session: DBSession
) -> TrainingReadSingle:
    training = session.exec(
        select(Training).where((Training.id == training_id) & (Training.creator_id == user.id))
    ).one_or_none()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")

    # Update only provided fields
    training_data = training_update.model_dump(exclude_unset=True)
    for key, value in training_data.items():
        setattr(training, key, value)

    training.updated_at = datetime.now(UTC).replace(tzinfo=None)
    session.add(training)
    session.commit()
    session.refresh(training)
    return training


@router.delete("/{training_id}", response_model=dict)
def delete_training(user: CurrentUser, training_id: UUID, session: DBSession) -> dict:
    training = session.exec(
        select(Training).where((Training.id == training_id) & (Training.creator_id == user.id))
    ).one_or_none()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training not found")

    # Delete the training
    session.delete(training)
    session.commit()
    return {"message": "training has been deleted"}
