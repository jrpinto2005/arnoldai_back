from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import ChatType


class ChatMessageBase(BaseModel):
    text: str


class GeneralChatRequest(ChatMessageBase):
    user_id: int


class SessionChatRequest(ChatMessageBase):
    user_id: int
    session_id: int


class ChatMessageOut(BaseModel):
    id: int
    user_id: int
    session_id: Optional[int]
    chat_type: ChatType
    role: str
    text: str
    audio_url: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: ChatMessageOut
