from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_current_active_user, get_db
from app.db.models import User, ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    ChatSessionCreate,
    ChatSession as ChatSessionSchema,
    ChatMessage as ChatMessageSchema,
    CoachingContext
)
from app.services.llm import LLMService
from app.services.elevenlabs_client import elevenlabs_client

router = APIRouter()
llm_service = LLMService()

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI coach and get a response"""
    
    # Get or create chat session
    if chat_request.session_id:
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == chat_request.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        # Create new session
        chat_session = ChatSession(
            user_id=current_user.id,
            session_name=f"Chat {len(db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()) + 1}",
            session_type=chat_request.session_type
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Save user message
    user_message = ChatMessage(
        chat_session_id=chat_session.id,
        content=chat_request.message,
        role="user",
        message_type="text"
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Build coaching context
    context = _build_coaching_context(current_user, chat_session, db)
    
    # Generate AI response
    ai_response_text = await llm_service.generate_chat_response(
        chat_request.message,
        context
    )
    
    # Save AI response
    ai_message = ChatMessage(
        chat_session_id=chat_session.id,
        content=ai_response_text,
        role="assistant",
        message_type="text"
    )
    db.add(ai_message)
    
    # Generate voice response if requested
    audio_url = None
    if chat_request.voice_enabled and elevenlabs_client.api_key:
        audio_url = await elevenlabs_client.text_to_speech(ai_response_text)
        if audio_url:
            ai_message.audio_url = audio_url
    
    db.commit()
    db.refresh(ai_message)
    
    # Update session timestamp
    chat_session.updated_at = ai_message.timestamp
    db.commit()
    db.refresh(chat_session)
    
    return ChatResponse(
        message=ai_message,
        session=chat_session,
        audio_url=audio_url
    )

@router.get("/sessions", response_model=list[ChatSessionSchema])
async def get_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user's chat sessions"""
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(
        ChatSession.updated_at.desc()
    ).offset(offset).limit(limit).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session with messages"""
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.post("/sessions", response_model=ChatSessionSchema)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    
    session = ChatSession(
        user_id=current_user.id,
        session_name=session_data.session_name,
        session_type=session_data.session_type
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageSchema])
async def get_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get messages from a chat session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(
        ChatMessage.timestamp.asc()
    ).offset(offset).limit(limit).all()
    
    return messages

def _build_coaching_context(user: User, chat_session: ChatSession, db: Session) -> CoachingContext:
    """Build coaching context for AI responses"""
    
    # Get recent workout sessions
    from app.db.models import WorkoutSession
    recent_workouts = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user.id
    ).order_by(WorkoutSession.created_at.desc()).limit(5).all()
    
    # Get conversation history (last 10 messages)
    conversation_history = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == chat_session.id
    ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    return CoachingContext(
        user_profile={
            "full_name": user.full_name,
            "age": user.age,
            "height": user.height,
            "weight": user.weight,
            "fitness_goal": user.fitness_goal,
            "activity_level": user.activity_level
        },
        recent_workouts=[
            {
                "name": w.name,
                "status": w.status,
                "workout_type": w.workout_type,
                "created_at": w.created_at,
                "completed_at": w.completed_at
            }
            for w in recent_workouts
        ],
        fitness_goals=[user.fitness_goal] if user.fitness_goal else [],
        current_session_type=chat_session.session_type,
        conversation_history=list(reversed(conversation_history))  # Chronological order
    )
