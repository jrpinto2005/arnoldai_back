# app/api/routes/metrics.py
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models

router = APIRouter(prefix="/users", tags=["metrics"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _compute_set_volume(workout_set: models.WorkoutSet) -> float:
    """
    Volumen simple de un set:
    - Si hay peso (actual o target): weight * reps.
    - Si no hay peso (ej. flexiones): usamos solo reps.
    """
    reps = workout_set.actual_reps or workout_set.target_reps or 0
    weight = workout_set.actual_weight or workout_set.target_weight

    if reps is None or reps <= 0:
        return 0.0

    if weight is None:
        # bodyweight u otros sin peso explícito: tomamos reps como volumen
        return float(reps)

    return float(weight) * float(reps)


# ---------------- Stats generales ----------------

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: int, db: Session = Depends(get_db_dep)):
    """
    Stats generales del usuario:
    - total_sessions
    - completed_sessions
    - completion_rate
    - total_volume (solo sesiones completadas)
    - last_session_date
    """
    _get_user_or_404(db, user_id)

    sessions = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.user_id == user_id)
        .all()
    )

    total_sessions = len(sessions)
    completed_sessions = [
        s for s in sessions if s.status == models.SessionStatus.COMPLETED
    ]

    # Volumen total de sesiones completadas
    total_volume = 0.0
    last_session_date = None

    for s in completed_sessions:
        if s.started_at and (last_session_date is None or s.started_at > last_session_date):
            last_session_date = s.started_at

        for wset in s.sets:
            total_volume += _compute_set_volume(wset)

    completion_rate = (
        len(completed_sessions) / total_sessions if total_sessions > 0 else 0.0
    )

    return {
        "user_id": user_id,
        "total_sessions": total_sessions,
        "completed_sessions": len(completed_sessions),
        "completion_rate": completion_rate,
        "total_volume": total_volume,
        "last_session_date": last_session_date,
    }


# ---------------- Progreso de fuerza ----------------

@router.get("/{user_id}/strength-progression")
async def get_strength_progression(user_id: int, db: Session = Depends(get_db_dep)):
    """
    Progreso de fuerza estimado por ejercicio, usando 1RM estimado:
    1RM ≈ peso * (1 + reps/30)
    Se toma el mejor set de cada sesión por ejercicio.
    """
    _get_user_or_404(db, user_id)

    # Sets con peso y reps de sesiones completadas
    sessions = (
        db.query(models.WorkoutSession)
        .filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.status == models.SessionStatus.COMPLETED,
        )
        .all()
    )

    # exercise_id -> { "name": ..., "points": [ {date, est_1rm}, ... ] }
    progression: Dict[int, Dict] = {}

    for session in sessions:
        if not session.started_at:
            continue

        # Para cada sesión, queremos el mejor set por ejercicio
        # ejercicio -> mejor 1RM en esa sesión
        best_in_session: Dict[int, float] = {}

        for wset in session.sets:
            # necesitamos reps y peso reales o target
            reps = wset.actual_reps or wset.target_reps
            weight = wset.actual_weight or wset.target_weight

            if not reps or not weight or reps <= 0 or weight <= 0:
                continue

            est_1rm = float(weight) * (1.0 + float(reps) / 30.0)

            current_best = best_in_session.get(wset.exercise_id)
            if current_best is None or est_1rm > current_best:
                best_in_session[wset.exercise_id] = est_1rm

        # Registrar en progression
        for ex_id, best_1rm in best_in_session.items():
            ex = db.query(models.Exercise).filter(models.Exercise.id == ex_id).first()
            if not ex:
                continue

            if ex_id not in progression:
                progression[ex_id] = {
                    "exercise_id": ex_id,
                    "exercise_name": ex.name,
                    "data": [],
                }

            progression[ex_id]["data"].append(
                {
                    "date": session.started_at,
                    "estimated_1rm": best_1rm,
                }
            )

    # Ordenar por fecha cada serie
    for ex_id in progression:
        progression[ex_id]["data"].sort(key=lambda p: p["date"])

    return {
        "user_id": user_id,
        "exercises": list(progression.values()),
    }


# ---------------- Consistencia semanal ----------------

@router.get("/{user_id}/consistency-analysis")
async def get_consistency_analysis(user_id: int, db: Session = Depends(get_db_dep)):
    """
    Analiza consistencia en las últimas 6 semanas:
    - sesiones por semana (usando ISO week)
    - promedio semanal
    - etiqueta: 'low', 'medium', 'high'
    """
    _get_user_or_404(db, user_id)

    today = datetime.utcnow().date()
    cutoff = today - timedelta(weeks=6)

    sessions = (
        db.query(models.WorkoutSession)
        .filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.started_at.isnot(None),
            models.WorkoutSession.started_at >= datetime.combine(cutoff, datetime.min.time()),
        )
        .all()
    )

    # (year, week) -> count
    per_week: Dict[tuple, int] = {}

    for s in sessions:
        if not s.started_at:
            continue
        dt = s.started_at.date()
        iso = dt.isocalendar()  # (year, week, weekday)
        key = (iso.year, iso.week)
        per_week[key] = per_week.get(key, 0) + 1

    # Convertir a lista ordenada
    weeks_data = []
    for (year, week), count in sorted(per_week.items()):
        weeks_data.append(
            {"year": year, "week": week, "sessions": count}
        )

    num_weeks = len(weeks_data) if weeks_data else 0
    total_sessions = len(sessions)
    avg_sessions = total_sessions / num_weeks if num_weeks > 0 else 0.0

    if avg_sessions >= 4:
        label = "high"
    elif avg_sessions >= 2:
        label = "medium"
    elif avg_sessions > 0:
        label = "low"
    else:
        label = "none"

    return {
        "user_id": user_id,
        "weeks": weeks_data,
        "average_sessions_per_week": avg_sessions,
        "consistency_label": label,
    }


# ---------------- Frecuencia por grupo muscular ----------------

@router.get("/{user_id}/muscle-group-frequency")
async def get_muscle_group_frequency(user_id: int, db: Session = Depends(get_db_dep)):
    """
    Frecuencia de entrenamiento por grupo muscular en los últimos 28 días.
    Cuenta en cuántas sesiones apareció cada grupo muscular.
    """
    _get_user_or_404(db, user_id)

    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=28)

    # Traer sets + session + exercise en la ventana
    sessions = (
        db.query(models.WorkoutSession)
        .filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.started_at.isnot(None),
            models.WorkoutSession.started_at >= datetime.combine(cutoff, datetime.min.time()),
        )
        .all()
    )

    # muscle_group -> set(session_ids)
    mg_sessions: Dict[str, set] = {}

    for s in sessions:
        for wset in s.sets:
            ex = wset.exercise
            if not ex:
                continue
            mg = ex.muscle_group or "unknown"
            if mg not in mg_sessions:
                mg_sessions[mg] = set()
            mg_sessions[mg].add(s.id)

    results = []
    for mg, sess_ids in mg_sessions.items():
        results.append(
            {
                "muscle_group": mg,
                "sessions_count": len(sess_ids),
            }
        )

    # ordenar por sesiones descendente
    results.sort(key=lambda x: x["sessions_count"], reverse=True)

    return {
        "user_id": user_id,
        "window_days": 28,
        "muscle_groups": results,
    }


# ---------------- Volumen por grupo muscular ----------------

@router.get("/{user_id}/volume-analysis")
async def get_volume_analysis(user_id: int, db: Session = Depends(get_db_dep)):
    """
    Análisis de volumen de entrenamiento por grupo muscular en los últimos 28 días.
    - volumen = peso * reps (o solo reps si no hay peso)
    - porcentaje relativo de volumen por grupo muscular
    """
    _get_user_or_404(db, user_id)

    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=28)

    sessions = (
        db.query(models.WorkoutSession)
        .filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.started_at.isnot(None),
            models.WorkoutSession.started_at >= datetime.combine(cutoff, datetime.min.time()),
            models.WorkoutSession.status == models.SessionStatus.COMPLETED,
        )
        .all()
    )

    mg_volume: Dict[str, float] = {}

    for s in sessions:
        for wset in s.sets:
            ex = wset.exercise
            if not ex:
                continue
            mg = ex.muscle_group or "unknown"
            vol = _compute_set_volume(wset)
            mg_volume[mg] = mg_volume.get(mg, 0.0) + vol

    total_volume = sum(mg_volume.values()) or 0.0

    results = []
    for mg, vol in mg_volume.items():
        pct = vol / total_volume if total_volume > 0 else 0.0
        results.append(
            {
                "muscle_group": mg,
                "volume": vol,
                "percentage": pct,
            }
        )

    # ordenar por volumen
    results.sort(key=lambda x: x["volume"], reverse=True)

    return {
        "user_id": user_id,
        "window_days": 28,
        "total_volume": total_volume,
        "muscle_groups": results,
    }
