from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db_dep
from app.db import models
from app.schemas.workout import (
    WorkoutSessionCreate,
    WorkoutSessionOut,
)
from app.services.planner import generate_session_plan_for_today

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/auto", response_model=WorkoutSessionOut)
def create_session_auto(
    user_id: int,
    db: Session = Depends(get_db_dep),
):
    """
    Crea una sesión nueva usando el planner (sin necesidad de que el cliente mande sets).
    Endpoint que puedes llamar después de que Arnold recomiende entrenar hoy.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sets_plan = generate_session_plan_for_today(db, user)

    session = models.WorkoutSession(
        user_id=user.id,
        status=models.SessionStatus.PLANNED,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Crear sets
    for s in sets_plan:
        ws = models.WorkoutSet(
            session_id=session.id,
            exercise_id=s.exercise_id,
            exercise_order=s.exercise_order,
            set_number=s.set_number,
            target_reps=s.target_reps,
            target_weight=s.target_weight,
        )
        db.add(ws)
    db.commit()
    db.refresh(session)

    return WorkoutSessionOut.model_validate(session)


@router.post("/", response_model=WorkoutSessionOut)
def create_session_manual(
    payload: WorkoutSessionCreate,
    db: Session = Depends(get_db_dep),
):
    """
    Alternativa: el front puede enviar ya los sets que decida (por ejemplo a partir del LLM).
    """
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = models.WorkoutSession(
        user_id=user.id,
        status=models.SessionStatus.PLANNED,
        fatigue_before=payload.fatigue_before,
        sleep_hours_last_night=payload.sleep_hours_last_night,
        notes=payload.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    for s in payload.sets:
        ws = models.WorkoutSet(
            session_id=session.id,
            exercise_id=s.exercise_id,
            exercise_order=s.exercise_order,
            set_number=s.set_number,
            target_reps=s.target_reps,
            target_weight=s.target_weight,
        )
        db.add(ws)
    db.commit()
    db.refresh(session)

    return WorkoutSessionOut.model_validate(session)


@router.get("/{session_id}", response_model=WorkoutSessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db_dep),
):
    session = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return WorkoutSessionOut.model_validate(session)


@router.post("/{session_id}/start", response_model=WorkoutSessionOut)
def start_session(
    session_id: int,
    db: Session = Depends(get_db_dep),
):
    session = db.query(models.WorkoutSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = models.SessionStatus.IN_PROGRESS
    session.started_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return WorkoutSessionOut.model_validate(session)


@router.post("/{session_id}/finish", response_model=WorkoutSessionOut)
def finish_session(
    session_id: int,
    db: Session = Depends(get_db_dep),
):
    session = db.query(models.WorkoutSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = models.SessionStatus.COMPLETED
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return WorkoutSessionOut.model_validate(session)
