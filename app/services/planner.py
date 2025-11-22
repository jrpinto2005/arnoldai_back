from sqlalchemy.orm import Session
from typing import List
from app.db import models
from app.schemas.workout import WorkoutSetCreate


def generate_session_plan_for_today(
    db: Session,
    user: models.User,
) -> List[WorkoutSetCreate]:
    """
    Crea una rutina muy simple para el día, en base al usuario.
    En el siguiente mensaje la hacemos más 'inteligente' usando historial.
    Por ahora: 3 ejercicios full body, 3x10.
    Debes tener ejercicios precargados en la tabla Exercise.
    """

    exercises = db.query(models.Exercise).limit(3).all()
    sets: List[WorkoutSetCreate] = []

    exercise_order = 1
    for ex in exercises:
        for s in range(1, 4):
            sets.append(
                WorkoutSetCreate(
                    exercise_id=ex.id,
                    exercise_order=exercise_order,
                    set_number=s,
                    target_reps=10,
                    target_weight=None,  # bodyweight / default
                )
            )
        exercise_order += 1

    return sets
