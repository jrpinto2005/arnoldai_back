from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.api.deps import get_current_active_user, get_db
from app.db.models import User, WorkoutSession, Exercise
from app.schemas.workout import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSession as WorkoutSessionSchema,
    WorkoutRecommendation,
    ExerciseCreate,
    ExerciseUpdate
)
from app.services.session_coach import SessionCoach
from app.services.planner import WorkoutPlanner

router = APIRouter()
session_coach = SessionCoach()
workout_planner = WorkoutPlanner()

@router.post("/start", response_model=dict)
async def start_workout_session(
    workout_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a workout session with AI coaching"""
    
    workout_session = db.query(WorkoutSession).filter(
        WorkoutSession.id == workout_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not workout_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    if workout_session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workout session already completed"
        )
    
    # Update session status and start time
    workout_session.status = "in_progress"
    workout_session.started_at = datetime.utcnow()
    db.commit()
    
    # Start coaching session
    coaching_data = await session_coach.start_coaching_session(
        current_user, 
        workout_session, 
        db
    )
    
    return coaching_data

@router.post("/create", response_model=WorkoutSessionSchema)
async def create_workout_session(
    workout_data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new workout session"""
    
    # Create workout session
    workout_session = WorkoutSession(
        user_id=current_user.id,
        name=workout_data.name,
        description=workout_data.description,
        workout_type=workout_data.workout_type,
        difficulty_level=workout_data.difficulty_level,
        scheduled_date=workout_data.scheduled_date,
        status="planned"
    )
    
    db.add(workout_session)
    db.commit()
    db.refresh(workout_session)
    
    # Add exercises
    for i, exercise_data in enumerate(workout_data.exercises):
        exercise = Exercise(
            workout_session_id=workout_session.id,
            name=exercise_data.name,
            exercise_type=exercise_data.exercise_type,
            sets=exercise_data.sets,
            reps=exercise_data.reps,
            weight=exercise_data.weight,
            duration_seconds=exercise_data.duration_seconds,
            rest_seconds=exercise_data.rest_seconds,
            notes=exercise_data.notes,
            order_in_workout=exercise_data.order_in_workout or i
        )
        db.add(exercise)
    
    db.commit()
    db.refresh(workout_session)
    
    return workout_session

@router.get("/", response_model=List[WorkoutSessionSchema])
async def get_workout_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get user's workout sessions"""
    
    query = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(WorkoutSession.status == status_filter)
    
    sessions = query.order_by(
        WorkoutSession.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return sessions

@router.get("/{session_id}", response_model=WorkoutSessionSchema)
async def get_workout_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific workout session"""
    
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    return session

@router.put("/{session_id}", response_model=WorkoutSessionSchema)
async def update_workout_session(
    session_id: int,
    session_update: WorkoutSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workout session"""
    
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    # Update fields
    for field, value in session_update.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/{session_id}/exercises/{exercise_id}/complete")
async def complete_exercise(
    session_id: int,
    exercise_id: int,
    performance_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark an exercise as completed with performance data"""
    
    # Verify session belongs to user
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    # Track completion with coaching
    completion_data = await session_coach.track_exercise_completion(
        current_user,
        exercise_id,
        performance_data,
        db
    )
    
    return completion_data

@router.post("/{session_id}/exercises/{exercise_id}/guidance")
async def get_exercise_guidance(
    session_id: int,
    exercise_id: int,
    guidance_type: str,  # form_check, motivation, modification
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI guidance for a specific exercise"""
    
    # Verify session belongs to user
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    guidance = await session_coach.provide_exercise_guidance(
        current_user,
        exercise_id,
        guidance_type,
        db
    )
    
    return guidance

@router.post("/{session_id}/exercises/{exercise_id}/difficulty")
async def report_exercise_difficulty(
    session_id: int,
    exercise_id: int,
    difficulty_data: Dict[str, str],  # {"type": "too_hard", "details": "..."}
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Report difficulty with an exercise and get adaptive recommendations"""
    
    # Verify session belongs to user
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    difficulty_type = difficulty_data.get("type", "form_issues")
    
    adaptation = await session_coach.handle_struggle_or_difficulty(
        current_user,
        exercise_id,
        difficulty_type,
        db
    )
    
    return adaptation

@router.post("/generate", response_model=WorkoutRecommendation)
async def generate_workout_plan(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized workout plan using AI"""
    
    user_profile = {
        "full_name": current_user.full_name,
        "age": current_user.age,
        "height": current_user.height,
        "weight": current_user.weight,
        "fitness_goal": current_user.fitness_goal,
        "activity_level": current_user.activity_level
    }
    
    recommendation = await workout_planner.create_personalized_plan(
        user_profile,
        preferences
    )
    
    return recommendation

@router.get("/{session_id}/coach/status")
async def get_coaching_status(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current coaching status and next exercise"""
    
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    # Get next exercise
    next_exercise = next(
        (ex for ex in session.exercises if not ex.is_completed),
        None
    )
    
    # Calculate progress
    total_exercises = len(session.exercises)
    completed_exercises = len([ex for ex in session.exercises if ex.is_completed])
    
    return {
        "session_id": session.id,
        "session_status": session.status,
        "next_exercise": {
            "id": next_exercise.id,
            "name": next_exercise.name,
            "sets": next_exercise.sets,
            "reps": next_exercise.reps,
            "notes": next_exercise.notes
        } if next_exercise else None,
        "progress": {
            "total_exercises": total_exercises,
            "completed_exercises": completed_exercises,
            "percentage": (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        },
        "session_duration_minutes": session.duration_minutes,
        "started_at": session.started_at
    }
