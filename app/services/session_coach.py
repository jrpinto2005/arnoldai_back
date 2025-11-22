from sqlalchemy.orm import Session
from app.db import models


def adjust_session_based_on_feedback(
    db: Session,
    session: models.WorkoutSession,
    user_message: str,
) -> None:
    """
    Regla súper simple para el MVP:
    - Si el usuario menciona 'pesado' o 'difícil' => bajar 5% peso en próximos sets sin completar.
    - Si menciona 'fácil' => subir 5%.
    Si no hay peso (bodyweight), no hace nada.
    """
    text = user_message.lower()
    factor = None

    if "pesado" in text or "difícil" in text or "muy duro" in text:
        factor = 0.95
    elif "fácil" in text or "muy fácil" in text or "ligero" in text:
        factor = 1.05

    if factor is None:
        return

    # Ajustar sets futuros (sin actual_reps aún)
    future_sets = (
        db.query(models.WorkoutSet)
        .filter(
            models.WorkoutSet.session_id == session.id,
            models.WorkoutSet.actual_reps.is_(None),
        )
        .all()
    )

    for s in future_sets:
        if s.target_weight is not None:
            s.target_weight = round(s.target_weight * factor, 1)
            s.auto_adjusted = True

    db.commit()
