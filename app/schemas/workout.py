from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExerciseBase(BaseModel):
    name: str
    exercise_type: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    order_in_workout: Optional[int] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    exercise_type: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    order_in_workout: Optional[int] = None
    is_completed: Optional[bool] = None

class Exercise(ExerciseBase):
    id: int
    workout_session_id: int
    is_completed: bool

    class Config:
        from_attributes = True

class WorkoutSessionBase(BaseModel):
    name: str
    description: Optional[str] = None
    workout_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    scheduled_date: Optional[datetime] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    exercises: List[ExerciseCreate] = []

class WorkoutSessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workout_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[float] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None

class WorkoutSession(WorkoutSessionBase):
    id: int
    user_id: int
    duration_minutes: Optional[int]
    calories_burned: Optional[float]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    exercises: List[Exercise] = []

    class Config:
        from_attributes = True

class WorkoutPlan(BaseModel):
    """Generated workout plan from AI"""
    name: str
    description: str
    workout_type: str
    difficulty_level: str
    estimated_duration: int
    exercises: List[ExerciseCreate]
    
class WorkoutRecommendation(BaseModel):
    """AI workout recommendation"""
    plan: WorkoutPlan
    rationale: str
    tips: List[str]
