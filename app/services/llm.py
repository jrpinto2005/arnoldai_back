import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.chat import ChatMessage, CoachingContext
from app.schemas.workout import WorkoutPlan, ExerciseCreate

class LLMService:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
    async def generate_chat_response(
        self, 
        user_message: str, 
        context: CoachingContext
    ) -> str:
        """Generate AI response for chat conversation"""
        
        if not settings.openai_api_key:
            return self._fallback_response(user_message, context)
        
        try:
            system_prompt = self._build_system_prompt(context)
            messages = self._build_conversation_history(context.conversation_history)
            messages.insert(0, {"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_response(user_message, context)
    
    async def generate_workout_plan(
        self, 
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> WorkoutPlan:
        """Generate personalized workout plan"""
        
        if not settings.openai_api_key:
            return self._fallback_workout_plan()
        
        try:
            prompt = self._build_workout_prompt(user_profile, preferences)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert fitness trainer. Create structured workout plans in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            # Parse response and convert to WorkoutPlan
            return self._parse_workout_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Workout generation error: {e}")
            return self._fallback_workout_plan()
    
    def _build_system_prompt(self, context: CoachingContext) -> str:
        """Build system prompt for AI assistant"""
        
        user_info = context.user_profile
        session_type = context.current_session_type
        
        base_prompt = f"""You are Arnold, an AI fitness coach and personal trainer. You are knowledgeable, motivating, and supportive.

User Profile:
- Name: {user_info.get('full_name', 'User')}
- Age: {user_info.get('age', 'Not provided')}
- Height: {user_info.get('height', 'Not provided')}cm
- Weight: {user_info.get('weight', 'Not provided')}kg
- Fitness Goal: {user_info.get('fitness_goal', 'Not specified')}
- Activity Level: {user_info.get('activity_level', 'Not specified')}

Session Type: {session_type}

Your responsibilities:
1. Provide personalized fitness advice and workout recommendations
2. Offer nutrition guidance and meal planning suggestions
3. Motivate and encourage users in their fitness journey
4. Answer questions about exercise form, techniques, and safety
5. Help users track progress and set realistic goals

Keep responses conversational, motivating, and actionable. If you need more information, ask specific questions."""
        
        if context.recent_workouts:
            base_prompt += f"\n\nRecent Workouts:\n"
            for workout in context.recent_workouts[-3:]:
                base_prompt += f"- {workout.get('name')} ({workout.get('status')})\n"
        
        return base_prompt
    
    def _build_conversation_history(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Convert chat messages to OpenAI format"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages[-10:]  # Last 10 messages for context
        ]
    
    def _build_workout_prompt(self, user_profile: Dict, preferences: Dict) -> str:
        """Build prompt for workout plan generation"""
        
        return f"""Create a personalized workout plan based on the following information:

User Profile:
- Age: {user_profile.get('age', 'Not provided')}
- Fitness Goal: {user_profile.get('fitness_goal', 'general fitness')}
- Activity Level: {user_profile.get('activity_level', 'moderate')}
- Available Time: {preferences.get('duration', 30)} minutes
- Equipment: {preferences.get('equipment', 'bodyweight')}
- Difficulty: {preferences.get('difficulty', 'intermediate')}

Please provide a structured workout plan with:
1. Workout name and description
2. List of exercises with sets, reps, and instructions
3. Estimated duration and difficulty level
4. Any safety tips or modifications

Format the response as JSON with the following structure:
{{
  "name": "Workout Name",
  "description": "Brief description",
  "workout_type": "strength/cardio/flexibility",
  "difficulty_level": "beginner/intermediate/advanced",
  "estimated_duration": 30,
  "exercises": [
    {{
      "name": "Exercise Name",
      "sets": 3,
      "reps": 12,
      "duration_seconds": null,
      "rest_seconds": 60,
      "notes": "Form tips and instructions"
    }}
  ]
}}"""
    
    def _parse_workout_response(self, response: str) -> WorkoutPlan:
        """Parse AI response into WorkoutPlan object"""
        # This would include JSON parsing logic
        # For now, return a basic plan
        return self._fallback_workout_plan()
    
    def _fallback_response(self, user_message: str, context: CoachingContext) -> str:
        """Fallback response when OpenAI is not available"""
        
        user_name = context.user_profile.get('full_name', 'there')
        
        responses = {
            "workout": f"Hi {user_name}! I'd love to help you plan your workout. To give you the best recommendations, could you tell me about your fitness goals and how much time you have available?",
            "nutrition": f"Great question about nutrition! For personalized meal planning, I'd need to know more about your goals. Are you looking to lose weight, gain muscle, or maintain your current fitness level?",
            "motivation": f"You've got this, {user_name}! Remember, consistency is key in fitness. Every workout counts, no matter how small. What's one thing you can do today to move closer to your goals?",
            "general": f"Hello {user_name}! I'm Arnold, your AI fitness coach. I'm here to help with workouts, nutrition, motivation, and any fitness questions you have. What would you like to work on today?"
        }
        
        # Simple keyword matching for response type
        message_lower = user_message.lower()
        if any(word in message_lower for word in ['workout', 'exercise', 'train']):
            return responses["workout"]
        elif any(word in message_lower for word in ['nutrition', 'diet', 'food', 'eat']):
            return responses["nutrition"]
        elif any(word in message_lower for word in ['motivation', 'help', 'struggle', 'hard']):
            return responses["motivation"]
        else:
            return responses["general"]
    
    def _fallback_workout_plan(self) -> WorkoutPlan:
        """Fallback workout plan when AI generation fails"""
        
        return WorkoutPlan(
            name="Basic Bodyweight Workout",
            description="A simple full-body workout using bodyweight exercises",
            workout_type="strength",
            difficulty_level="beginner",
            estimated_duration=30,
            exercises=[
                ExerciseCreate(
                    name="Push-ups",
                    sets=3,
                    reps=10,
                    rest_seconds=60,
                    notes="Keep your core tight and lower your chest to the ground"
                ),
                ExerciseCreate(
                    name="Bodyweight Squats",
                    sets=3,
                    reps=15,
                    rest_seconds=60,
                    notes="Sit back like you're sitting in a chair, keep your chest up"
                ),
                ExerciseCreate(
                    name="Plank",
                    duration_seconds=30,
                    sets=3,
                    rest_seconds=60,
                    notes="Hold a straight line from head to heels"
                ),
                ExerciseCreate(
                    name="Mountain Climbers",
                    duration_seconds=30,
                    sets=3,
                    rest_seconds=60,
                    notes="Keep your core engaged and alternate legs quickly"
                )
            ]
        )
