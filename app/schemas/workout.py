from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.db.models import SessionStatus


class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    equipment: Optional[str] = None
    level: Optional[str] = None


class ExerciseOut(ExerciseBase):
    id: int

    class Config:
        from_attributes = True


class WorkoutSetBase(BaseModel):
    exercise_id: int
    exercise_order: int
    set_number: int
    target_reps: int
    target_weight: Optional[float] = None


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSetOut(WorkoutSetBase):
    id: int
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    rpe: Optional[float] = None
    comment: Optional[str] = None
    auto_adjusted: bool

    class Config:
        from_attributes = True


class WorkoutSessionCreate(BaseModel):
    user_id: int
    fatigue_before: Optional[float] = None
    sleep_hours_last_night: Optional[float] = None
    notes: Optional[str] = None
    # aquí podrías recibir directamente los sets sugeridos por el planner
    sets: List[WorkoutSetCreate]


class WorkoutSessionOut(BaseModel):
    id: int
    user_id: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: SessionStatus
    fatigue_before: Optional[float]
    sleep_hours_last_night: Optional[float]
    notes: Optional[str]
    sets: List[WorkoutSetOut]

    class Config:
        from_attributes = True
