from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str
    role: str  # user, assistant, system
    message_type: str = "text"  # text, audio, image

class ChatMessageCreate(ChatMessageBase):
    audio_data: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(ChatMessageBase):
    id: int
    chat_session_id: int
    audio_url: Optional[str]
    metadata: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    session_name: Optional[str] = None
    session_type: str = "general"  # general, workout_planning, nutrition, motivation

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    voice_enabled: bool = False
    session_type: str = "general"

class ChatResponse(BaseModel):
    message: ChatMessage
    session: ChatSession
    audio_url: Optional[str] = None

class VoiceMessageRequest(BaseModel):
    audio_data: bytes
    session_id: Optional[int] = None

class CoachingContext(BaseModel):
    """Context for AI coaching decisions"""
    user_profile: Dict[str, Any]
    recent_workouts: List[Dict[str, Any]]
    fitness_goals: List[str]
    current_session_type: str
    conversation_history: List[ChatMessage]
