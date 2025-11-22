from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.schemas.workout import WorkoutPlan, WorkoutRecommendation, ExerciseCreate
from app.services.llm import LLMService

class WorkoutPlanner:
    def __init__(self):
        self.llm_service = LLMService()
    
    async def create_personalized_plan(
        self, 
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> WorkoutRecommendation:
        """Create a personalized workout plan"""
        
        # Generate workout plan using AI
        workout_plan = await self.llm_service.generate_workout_plan(
            user_profile, 
            preferences
        )
        
        # Generate rationale and tips
        rationale = self._generate_rationale(user_profile, preferences, workout_plan)
        tips = self._generate_tips(user_profile, workout_plan)
        
        return WorkoutRecommendation(
            plan=workout_plan,
            rationale=rationale,
            tips=tips
        )
    
    def create_progressive_plan(
        self, 
        user_profile: Dict[str, Any],
        current_week: int,
        total_weeks: int = 12
    ) -> WorkoutPlan:
        """Create progressive workout plan that increases in difficulty"""
        
        base_difficulty = user_profile.get('fitness_level', 'beginner')
        fitness_goal = user_profile.get('fitness_goal', 'general_fitness')
        
        # Calculate progression factor
        progression_factor = min(current_week / total_weeks, 1.0)
        
        if fitness_goal == 'weight_loss':
            return self._create_weight_loss_plan(progression_factor)
        elif fitness_goal == 'muscle_gain':
            return self._create_muscle_gain_plan(progression_factor)
        elif fitness_goal == 'endurance':
            return self._create_endurance_plan(progression_factor)
        else:
            return self._create_general_fitness_plan(progression_factor)
    
    def adapt_plan_to_equipment(
        self, 
        base_plan: WorkoutPlan, 
        available_equipment: List[str]
    ) -> WorkoutPlan:
        """Adapt workout plan based on available equipment"""
        
        equipment_substitutions = {
            'dumbbells': {
                'push_ups': 'dumbbell_press',
                'bodyweight_squats': 'dumbbell_squats',
                'lunges': 'dumbbell_lunges'
            },
            'resistance_bands': {
                'pull_ups': 'band_pull_aparts',
                'lat_pulldowns': 'band_lat_pulls'
            },
            'kettlebells': {
                'deadlifts': 'kettlebell_deadlifts',
                'rows': 'kettlebell_rows'
            }
        }
        
        adapted_exercises = []
        for exercise in base_plan.exercises:
            adapted_exercise = exercise
            
            # Check if we can upgrade the exercise based on equipment
            for equipment, substitutions in equipment_substitutions.items():
                if equipment in available_equipment:
                    for old_exercise, new_exercise in substitutions.items():
                        if old_exercise.lower() in exercise.name.lower():
                            adapted_exercise.name = new_exercise.replace('_', ' ').title()
                            break
            
            adapted_exercises.append(adapted_exercise)
        
        return WorkoutPlan(
            name=base_plan.name + " (Equipment Adapted)",
            description=base_plan.description,
            workout_type=base_plan.workout_type,
            difficulty_level=base_plan.difficulty_level,
            estimated_duration=base_plan.estimated_duration,
            exercises=adapted_exercises
        )
    
    def _generate_rationale(
        self, 
        user_profile: Dict[str, Any], 
        preferences: Dict[str, Any],
        plan: WorkoutPlan
    ) -> str:
        """Generate rationale for the workout plan"""
        
        goal = user_profile.get('fitness_goal', 'general fitness')
        level = user_profile.get('activity_level', 'moderate')
        
        rationale_templates = {
            'weight_loss': f"This {plan.workout_type} workout is designed for weight loss with high-intensity exercises that boost metabolism. Perfect for your {level} activity level.",
            'muscle_gain': f"This strength-focused routine targets major muscle groups to promote muscle growth. The rep ranges are optimized for hypertrophy based on your {level} experience level.",
            'endurance': f"This cardio-focused plan builds cardiovascular endurance while maintaining strength. Great for improving your overall {level} fitness level.",
            'general_fitness': f"This balanced workout combines strength and cardio elements for overall fitness improvement, suitable for your {level} activity level."
        }
        
        return rationale_templates.get(goal, rationale_templates['general_fitness'])
    
    def _generate_tips(self, user_profile: Dict[str, Any], plan: WorkoutPlan) -> List[str]:
        """Generate workout tips based on plan and user profile"""
        
        base_tips = [
            "Focus on proper form over speed or weight",
            "Stay hydrated throughout your workout",
            "Listen to your body and rest if you feel pain"
        ]
        
        if plan.workout_type == 'strength':
            base_tips.extend([
                "Progressive overload is key - gradually increase weight or reps",
                "Allow 48-72 hours rest between training the same muscle groups"
            ])
        elif plan.workout_type == 'cardio':
            base_tips.extend([
                "Maintain a pace where you can still hold a conversation",
                "Cool down with light stretching after your session"
            ])
        
        # Add beginner-specific tips
        if user_profile.get('activity_level') == 'sedentary':
            base_tips.append("Start slowly and gradually increase intensity as you build fitness")
        
        return base_tips
    
    def _create_weight_loss_plan(self, progression_factor: float) -> WorkoutPlan:
        """Create a weight loss focused workout plan"""
        
        base_duration = int(25 + (progression_factor * 15))  # 25-40 minutes
        intensity_multiplier = 1 + (progression_factor * 0.5)
        
        exercises = [
            ExerciseCreate(
                name="Jumping Jacks",
                duration_seconds=int(30 * intensity_multiplier),
                sets=3,
                rest_seconds=30,
                notes="High-intensity cardio to boost heart rate"
            ),
            ExerciseCreate(
                name="Burpees",
                sets=3,
                reps=int(8 + progression_factor * 7),  # 8-15 reps
                rest_seconds=45,
                notes="Full-body exercise for maximum calorie burn"
            ),
            ExerciseCreate(
                name="High Knees",
                duration_seconds=int(30 * intensity_multiplier),
                sets=3,
                rest_seconds=30,
                notes="Maintain quick, controlled movements"
            ),
            ExerciseCreate(
                name="Mountain Climbers",
                duration_seconds=int(45 * intensity_multiplier),
                sets=3,
                rest_seconds=30,
                notes="Keep core engaged throughout"
            )
        ]
        
        return WorkoutPlan(
            name="Fat Burning HIIT",
            description="High-intensity interval training for maximum calorie burn",
            workout_type="cardio",
            difficulty_level="intermediate",
            estimated_duration=base_duration,
            exercises=exercises
        )
    
    def _create_muscle_gain_plan(self, progression_factor: float) -> WorkoutPlan:
        """Create a muscle gain focused workout plan"""
        
        base_reps = int(8 + progression_factor * 4)  # 8-12 reps
        base_sets = int(3 + progression_factor * 1)  # 3-4 sets
        
        exercises = [
            ExerciseCreate(
                name="Push-ups",
                sets=base_sets,
                reps=base_reps,
                rest_seconds=90,
                notes="Focus on controlled movement and full range of motion"
            ),
            ExerciseCreate(
                name="Squats",
                sets=base_sets,
                reps=base_reps,
                rest_seconds=90,
                notes="Keep chest up and sit back into the squat"
            ),
            ExerciseCreate(
                name="Pike Push-ups",
                sets=base_sets,
                reps=int(base_reps * 0.8),
                rest_seconds=90,
                notes="Targets shoulders and upper chest"
            ),
            ExerciseCreate(
                name="Single-leg Glute Bridges",
                sets=base_sets,
                reps=base_reps,
                rest_seconds=60,
                notes="Squeeze glutes at the top of each rep"
            )
        ]
        
        return WorkoutPlan(
            name="Strength Builder",
            description="Bodyweight strength training for muscle development",
            workout_type="strength",
            difficulty_level="intermediate",
            estimated_duration=40,
            exercises=exercises
        )
    
    def _create_endurance_plan(self, progression_factor: float) -> WorkoutPlan:
        """Create an endurance focused workout plan"""
        
        base_duration = int(45 + progression_factor * 30)  # 45-75 seconds
        
        exercises = [
            ExerciseCreate(
                name="Marching in Place",
                duration_seconds=base_duration,
                sets=4,
                rest_seconds=30,
                notes="Maintain steady rhythm and good posture"
            ),
            ExerciseCreate(
                name="Wall Sit",
                duration_seconds=int(base_duration * 0.7),
                sets=3,
                rest_seconds=60,
                notes="Keep back flat against wall"
            ),
            ExerciseCreate(
                name="Step-ups",
                duration_seconds=base_duration,
                sets=3,
                rest_seconds=45,
                notes="Use a stable surface, alternate legs"
            ),
            ExerciseCreate(
                name="Arm Circles",
                duration_seconds=base_duration,
                sets=2,
                rest_seconds=30,
                notes="Large circles, forward and backward"
            )
        ]
        
        return WorkoutPlan(
            name="Endurance Builder",
            description="Low-impact exercises to build cardiovascular endurance",
            workout_type="cardio",
            difficulty_level="beginner",
            estimated_duration=35,
            exercises=exercises
        )
    
    def _create_general_fitness_plan(self, progression_factor: float) -> WorkoutPlan:
        """Create a general fitness workout plan"""
        
        base_reps = int(10 + progression_factor * 5)  # 10-15 reps
        
        exercises = [
            ExerciseCreate(
                name="Bodyweight Squats",
                sets=3,
                reps=base_reps,
                rest_seconds=60,
                notes="Full range of motion, control the descent"
            ),
            ExerciseCreate(
                name="Push-ups",
                sets=3,
                reps=int(base_reps * 0.8),
                rest_seconds=60,
                notes="Modify on knees if needed"
            ),
            ExerciseCreate(
                name="Plank",
                duration_seconds=int(30 + progression_factor * 30),
                sets=3,
                rest_seconds=60,
                notes="Maintain straight line from head to heels"
            ),
            ExerciseCreate(
                name="Lunges",
                sets=3,
                reps=int(base_reps * 0.8),  # Each leg
                rest_seconds=60,
                notes="Step forward, lower back knee toward ground"
            )
        ]
        
        return WorkoutPlan(
            name="Balanced Fitness",
            description="Well-rounded workout combining strength and stability",
            workout_type="mixed",
            difficulty_level="beginner",
            estimated_duration=30,
            exercises=exercises
        )
