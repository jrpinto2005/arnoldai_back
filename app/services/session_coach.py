from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import User, WorkoutSession, ChatSession
from app.schemas.workout import WorkoutSessionCreate, WorkoutRecommendation
from app.schemas.chat import CoachingContext
from app.services.llm import LLMService
from app.services.planner import WorkoutPlanner
from app.services.elevenlabs_client import elevenlabs_client

class SessionCoach:
    """AI coach that provides real-time guidance during workout sessions"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.planner = WorkoutPlanner()
    
    async def start_coaching_session(
        self, 
        user: User, 
        workout_session: WorkoutSession,
        db: Session
    ) -> Dict[str, Any]:
        """Start a new coaching session"""
        
        # Create context for the session
        context = self._build_coaching_context(user, workout_session, db)
        
        # Generate welcome message
        welcome_message = await self._generate_welcome_message(context)
        
        # Generate motivational audio if enabled
        audio_url = await elevenlabs_client.generate_motivational_audio(
            user.full_name or user.username,
            f"started {workout_session.name}"
        )
        
        return {
            "session_id": workout_session.id,
            "welcome_message": welcome_message,
            "audio_url": audio_url,
            "next_exercise": self._get_next_exercise(workout_session),
            "session_stats": self._get_session_stats(workout_session)
        }
    
    async def provide_exercise_guidance(
        self,
        user: User,
        exercise_id: int,
        request_type: str,  # "form_check", "motivation", "modification"
        db: Session
    ) -> Dict[str, Any]:
        """Provide specific guidance for an exercise"""
        
        exercise = self._get_exercise_by_id(exercise_id, db)
        if not exercise:
            return {"error": "Exercise not found"}
        
        guidance_prompts = {
            "form_check": f"Provide form tips and safety guidelines for {exercise.name}",
            "motivation": f"Give motivational encouragement for completing {exercise.name}",
            "modification": f"Suggest easier or harder modifications for {exercise.name}"
        }
        
        prompt = guidance_prompts.get(request_type, guidance_prompts["form_check"])
        
        # Build context
        context = self._build_exercise_context(user, exercise, db)
        
        # Generate response
        response = await self.llm_service.generate_chat_response(prompt, context)
        
        # Generate audio if it's motivation
        audio_url = None
        if request_type == "motivation":
            audio_url = await elevenlabs_client.text_to_speech(response)
        
        return {
            "guidance": response,
            "audio_url": audio_url,
            "exercise_info": {
                "name": exercise.name,
                "sets": exercise.sets,
                "reps": exercise.reps,
                "notes": exercise.notes
            }
        }
    
    async def track_exercise_completion(
        self,
        user: User,
        exercise_id: int,
        performance_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Track when user completes an exercise"""
        
        exercise = self._get_exercise_by_id(exercise_id, db)
        if not exercise:
            return {"error": "Exercise not found"}
        
        # Update exercise completion
        exercise.is_completed = True
        
        # Record performance data if provided
        if performance_data:
            if "actual_reps" in performance_data:
                exercise.reps = performance_data["actual_reps"]
            if "actual_weight" in performance_data:
                exercise.weight = performance_data["actual_weight"]
            if "notes" in performance_data:
                exercise.notes = (exercise.notes or "") + f" | Completed: {performance_data['notes']}"
        
        db.commit()
        
        # Generate congratulatory message
        congratulations = await self._generate_completion_message(user, exercise)
        
        # Check if workout is complete
        workout_session = exercise.workout_session
        remaining_exercises = [ex for ex in workout_session.exercises if not ex.is_completed]
        
        response_data = {
            "congratulations": congratulations,
            "exercise_completed": True,
            "remaining_exercises": len(remaining_exercises)
        }
        
        if not remaining_exercises:
            # Workout complete!
            completion_data = await self._complete_workout_session(workout_session, db)
            response_data.update(completion_data)
        else:
            # Get next exercise
            response_data["next_exercise"] = self._get_next_exercise_info(remaining_exercises[0])
        
        return response_data
    
    async def provide_rest_guidance(
        self,
        user: User,
        current_exercise_id: int,
        rest_seconds: int,
        db: Session
    ) -> Dict[str, Any]:
        """Provide guidance during rest periods"""
        
        exercise = self._get_exercise_by_id(current_exercise_id, db)
        
        if rest_seconds > 60:
            # Long rest - provide tips or light motivation
            message = await self.llm_service.generate_chat_response(
                f"Give brief motivation during {rest_seconds} second rest after {exercise.name}",
                self._build_exercise_context(user, exercise, db)
            )
        else:
            # Short rest - simple encouragement
            message = f"Great job on {exercise.name}! Take {rest_seconds} seconds to recover and prepare for the next exercise."
        
        return {
            "rest_guidance": message,
            "rest_duration": rest_seconds,
            "breathing_tip": "Focus on deep, controlled breathing to optimize recovery"
        }
    
    async def handle_struggle_or_difficulty(
        self,
        user: User,
        exercise_id: int,
        difficulty_type: str,  # "too_easy", "too_hard", "form_issues", "pain"
        db: Session
    ) -> Dict[str, Any]:
        """Handle when user reports difficulty with exercise"""
        
        exercise = self._get_exercise_by_id(exercise_id, db)
        
        if difficulty_type == "pain":
            return {
                "message": "Stop the exercise immediately. Pain is not normal during workouts. Consider consulting a healthcare professional if pain persists.",
                "recommendation": "skip_exercise",
                "alternative": None
            }
        
        # Generate adaptive recommendations
        context = self._build_exercise_context(user, exercise, db)
        
        prompts = {
            "too_easy": f"Suggest progressions to make {exercise.name} more challenging",
            "too_hard": f"Suggest modifications to make {exercise.name} easier",
            "form_issues": f"Provide detailed form corrections for {exercise.name}"
        }
        
        recommendation = await self.llm_service.generate_chat_response(
            prompts.get(difficulty_type, prompts["form_issues"]),
            context
        )
        
        return {
            "message": recommendation,
            "recommendation": "modify_exercise",
            "difficulty_type": difficulty_type
        }
    
    def _build_coaching_context(self, user: User, workout_session: WorkoutSession, db: Session) -> CoachingContext:
        """Build context for coaching session"""
        
        # Get recent workout history
        recent_workouts = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.id != workout_session.id
        ).order_by(WorkoutSession.created_at.desc()).limit(5).all()
        
        return CoachingContext(
            user_profile={
                "full_name": user.full_name,
                "age": user.age,
                "fitness_goal": user.fitness_goal,
                "activity_level": user.activity_level
            },
            recent_workouts=[
                {
                    "name": w.name,
                    "status": w.status,
                    "workout_type": w.workout_type,
                    "completed_at": w.completed_at
                }
                for w in recent_workouts
            ],
            fitness_goals=[user.fitness_goal] if user.fitness_goal else [],
            current_session_type="workout_coaching",
            conversation_history=[]
        )
    
    def _build_exercise_context(self, user: User, exercise, db: Session) -> CoachingContext:
        """Build context for exercise-specific guidance"""
        
        return CoachingContext(
            user_profile={
                "full_name": user.full_name,
                "fitness_goal": user.fitness_goal,
                "activity_level": user.activity_level
            },
            recent_workouts=[],
            fitness_goals=[user.fitness_goal] if user.fitness_goal else [],
            current_session_type="exercise_guidance",
            conversation_history=[]
        )
    
    async def _generate_welcome_message(self, context: CoachingContext) -> str:
        """Generate personalized welcome message for workout session"""
        
        user_name = context.user_profile.get("full_name", "Champion")
        
        welcome_templates = [
            f"Welcome back, {user_name}! Ready to crush this workout? I'll be here to guide you through every rep!",
            f"Let's do this, {user_name}! Today's session is going to be amazing. I'm here to help you succeed!",
            f"Great to see you, {user_name}! Time to show this workout who's boss. Let's get started!"
        ]
        
        import random
        return random.choice(welcome_templates)
    
    async def _generate_completion_message(self, user: User, exercise) -> str:
        """Generate congratulatory message for exercise completion"""
        
        user_name = user.full_name or user.username
        
        messages = [
            f"Excellent work on those {exercise.name}, {user_name}! You're crushing it!",
            f"Outstanding job, {user_name}! Those {exercise.name} were perfect!",
            f"Fantastic effort, {user_name}! You just dominated that exercise!",
            f"Great job, {user_name}! Your form on {exercise.name} was spot on!"
        ]
        
        import random
        return random.choice(messages)
    
    async def _complete_workout_session(self, workout_session: WorkoutSession, db: Session) -> Dict[str, Any]:
        """Handle workout session completion"""
        
        workout_session.status = "completed"
        workout_session.completed_at = datetime.utcnow()
        
        # Calculate total duration
        if workout_session.started_at:
            duration = datetime.utcnow() - workout_session.started_at
            workout_session.duration_minutes = int(duration.total_seconds() / 60)
        
        db.commit()
        
        # Generate completion audio
        user = workout_session.user
        audio_url = await elevenlabs_client.generate_motivational_audio(
            user.full_name or user.username,
            f"completed {workout_session.name}"
        )
        
        return {
            "workout_completed": True,
            "completion_message": f"Incredible work! You've completed {workout_session.name}. That's the dedication of a true champion!",
            "audio_url": audio_url,
            "session_summary": {
                "duration_minutes": workout_session.duration_minutes,
                "exercises_completed": len([ex for ex in workout_session.exercises if ex.is_completed]),
                "total_exercises": len(workout_session.exercises)
            }
        }
    
    def _get_next_exercise(self, workout_session: WorkoutSession) -> Optional[Dict[str, Any]]:
        """Get the next exercise to perform"""
        
        next_exercise = next(
            (ex for ex in workout_session.exercises if not ex.is_completed),
            None
        )
        
        if next_exercise:
            return self._get_next_exercise_info(next_exercise)
        
        return None
    
    def _get_next_exercise_info(self, exercise) -> Dict[str, Any]:
        """Get exercise information"""
        
        return {
            "id": exercise.id,
            "name": exercise.name,
            "sets": exercise.sets,
            "reps": exercise.reps,
            "duration_seconds": exercise.duration_seconds,
            "rest_seconds": exercise.rest_seconds,
            "notes": exercise.notes,
            "exercise_type": exercise.exercise_type
        }
    
    def _get_session_stats(self, workout_session: WorkoutSession) -> Dict[str, Any]:
        """Get current session statistics"""
        
        total_exercises = len(workout_session.exercises)
        completed_exercises = len([ex for ex in workout_session.exercises if ex.is_completed])
        
        return {
            "total_exercises": total_exercises,
            "completed_exercises": completed_exercises,
            "progress_percentage": (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0,
            "estimated_duration": workout_session.duration_minutes or 30
        }
    
    def _get_exercise_by_id(self, exercise_id: int, db: Session):
        """Get exercise by ID"""
        from app.db.models import Exercise
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()
