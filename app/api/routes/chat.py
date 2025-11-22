from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.schemas.chat import (
    GeneralChatRequest,
    SessionChatRequest,
    ChatMessageOut,
    ChatResponse,
)
from app.db.models import ChatType
from app.services.llm import generate_arnold_response
from app.services.elevenlabs_client import tts_generate_audio_url
from app.services.session_coach import adjust_session_based_on_feedback

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/general", response_model=ChatResponse)
async def general_chat(
    payload: GeneralChatRequest,
    db: Session = Depends(get_db_dep),
):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Guardamos el mensaje del usuario
    user_msg = models.ChatMessage(
        user_id=user.id,
        session_id=None,
        chat_type=ChatType.GENERAL,
        role="user",
        text=payload.text,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Para el MVP, enviamos solo el mensaje actual al LLM
    arnold_text = await generate_arnold_response(
        messages=[{"role": "user", "content": payload.text}],
        mode="general",
    )

    audio_url = await tts_generate_audio_url(arnold_text)

    arnold_msg = models.ChatMessage(
        user_id=user.id,
        session_id=None,
        chat_type=ChatType.GENERAL,
        role="arnold",
        text=arnold_text,
        audio_url=audio_url,
    )
    db.add(arnold_msg)
    db.commit()
    db.refresh(arnold_msg)

    return ChatResponse(message=ChatMessageOut.model_validate(arnold_msg))


@router.post("/session", response_model=ChatResponse)
async def session_chat(
    payload: SessionChatRequest,
    db: Session = Depends(get_db_dep),
):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.id == payload.session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Guardamos mensaje del usuario
    user_msg = models.ChatMessage(
        user_id=user.id,
        session_id=session.id,
        chat_type=ChatType.SESSION,
        role="user",
        text=payload.text,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Aplicar lógica de ajuste de sesión según feedback
    adjust_session_based_on_feedback(db, session, payload.text)

    arnold_text = await generate_arnold_response(
        messages=[{"role": "user", "content": payload.text}],
        mode="session",
    )

    audio_url = await tts_generate_audio_url(arnold_text)

    arnold_msg = models.ChatMessage(
        user_id=user.id,
        session_id=session.id,
        chat_type=ChatType.SESSION,
        role="arnold",
        text=arnold_text,
        audio_url=audio_url,
    )
    db.add(arnold_msg)
    db.commit()
    db.refresh(arnold_msg)

    return ChatResponse(message=ChatMessageOut.model_validate(arnold_msg))
