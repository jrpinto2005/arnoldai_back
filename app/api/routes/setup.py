from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models

router = APIRouter(prefix="/setup", tags=["setup"])


@router.post("/seed")
def seed_data(db: Session = Depends(get_db_dep)):
    """
    Crea un usuario demo y algunos ejercicios básicos si no existen.
    Ideal para la hackatón: POST /setup/seed una vez y listo.
    """

    # Usuario demo
    user = db.query(models.User).filter_by(name="Demo User").first()
    if not user:
        user = models.User(
            name="Demo User",
            goal="hypertrophy",
            experience_level="intermediate",
            weight_kg=75,
            height_cm=175,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Algunos ejercicios básicos
    default_exercises = [
        ("Bench Press", "chest", "barbell", "intermediate"),
        ("Squat", "legs", "barbell", "intermediate"),
        ("Deadlift", "back", "barbell", "intermediate"),
        ("Overhead Press", "shoulders", "barbell", "intermediate"),
        ("Lat Pulldown", "back", "machine", "beginner"),
        ("Leg Press", "legs", "machine", "beginner"),
    ]

    created = 0
    for name, group, equip, level in default_exercises:
        ex = db.query(models.Exercise).filter_by(name=name).first()
        if not ex:
            ex = models.Exercise(
                name=name,
                muscle_group=group,
                equipment=equip,
                level=level,
            )
            db.add(ex)
            created += 1

    if created:
        db.commit()

    return {
        "message": "Seed completed",
        "user_id": user.id,
        "new_exercises_created": created,
    }
