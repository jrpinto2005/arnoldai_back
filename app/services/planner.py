from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.db import models
from app.schemas.workout import WorkoutSetCreate


def _get_least_trained_muscle_group(db: Session, user_id: int) -> str:
    """
    Mira los últimos 7 días y calcula volumen por grupo muscular.
    Devuelve el grupo menos trabajado.
    Si no hay historial, devuelve 'full_body'.
    """

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # join entre WorkoutSet, WorkoutSession y Exercise
    q = (
        db.query(
            models.Exercise.muscle_group,
            func.sum(
                (models.WorkoutSet.actual_weight or models.WorkoutSet.target_weight or 0)
                * (models.WorkoutSet.actual_reps or models.WorkoutSet.target_reps or 0)
            ).label("volume"),
        )
        .join(models.WorkoutSession, models.WorkoutSession.id == models.WorkoutSet.session_id)
        .join(models.Exercise, models.Exercise.id == models.WorkoutSet.exercise_id)
        .filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.started_at >= seven_days_ago,
            models.WorkoutSession.status == models.SessionStatus.COMPLETED,
        )
        .group_by(models.Exercise.muscle_group)
    )

    volumes = q.all()

    if not volumes:
        return "full_body"

    # Encontrar grupo con menor volumen
    least = min(volumes, key=lambda x: x.volume or 0)
    return least.muscle_group


def generate_session_plan_for_today(
    db: Session,
    user: models.User,
) -> List[WorkoutSetCreate]:
    """
    Genera una rutina simple en función del grupo menos trabajado.
    - Si es 'full_body' -> mezcla.
    - Si ya hay historial, prioriza ese grupo muscular.
    """

    target_group = _get_least_trained_muscle_group(db, user.id)

    if target_group == "full_body":
        # Tomar 3 ejercicios variados
        exercises = (
            db.query(models.Exercise)
            .order_by(models.Exercise.muscle_group)
            .limit(3)
            .all()
        )
    else:
        # Priorizar el grupo menos trabajado, y llenar con otros
        main_ex = (
            db.query(models.Exercise)
            .filter(models.Exercise.muscle_group == target_group)
            .limit(2)
            .all()
        )
        others = (
            db.query(models.Exercise)
            .filter(models.Exercise.muscle_group != target_group)
            .limit(1)
            .all()
        )
        exercises = main_ex + others

    if not exercises:
        # fallback por si acaso
        exercises = db.query(models.Exercise).limit(3).all()

    sets: List[WorkoutSetCreate] = []

    exercise_order = 1
    for ex in exercises:
        # 3 series de 8–12 reps (dejamos fijo 10 para MVP)
        for s in range(1, 4):
            sets.append(
                WorkoutSetCreate(
                    exercise_id=ex.id,
                    exercise_order=exercise_order,
                    set_number=s,
                    target_reps=10,
                    target_weight=None,  # para el demo, el usuario puede setear peso en el front
                )
            )
        exercise_order += 1

    return sets
