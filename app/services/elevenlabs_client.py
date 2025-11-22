from elevenlabs import generate, save, Voice
from typing import Optional
import tempfile
import os
from app.core.config import settings

class ElevenLabsClient:
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = "ErXwobaYiN019PkySvjV"  # Arnold Schwarzenegger-like voice
        
    async def text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech using ElevenLabs"""
        
        if not self.api_key:
            return None
            
        try:
            # Generate audio from text
            audio = generate(
                text=text,
                voice=Voice(voice_id=self.voice_id),
                model="eleven_multilingual_v2"
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio)
                return temp_file.name
                
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return None
    
    async def generate_motivational_audio(self, user_name: str, achievement: str) -> Optional[str]:
        """Generate motivational audio message"""
        
        motivational_texts = [
            f"Outstanding work, {user_name}! You just {achievement}. That's what champions are made of!",
            f"Excellent job on {achievement}, {user_name}! You're crushing your goals like a true warrior!",
            f"Fantastic effort, {user_name}! {achievement} shows your dedication. Keep pushing forward!",
            f"Incredible work, {user_name}! You just {achievement}. I'm proud of your commitment!"
        ]
        
        import random
        text = random.choice(motivational_texts)
        
        return await self.text_to_speech(text)
    
    def cleanup_audio_file(self, file_path: str):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up audio file: {e}")

# Global instance
elevenlabs_client = ElevenLabsClient()
