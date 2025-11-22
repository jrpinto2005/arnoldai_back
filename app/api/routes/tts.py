from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.services.elevenlabs_client import tts_generate_audio_url
from app.core.config import settings

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str


class TTSResponse(BaseModel):
    audio_url: str | None


@router.post("/test", response_model=TTSResponse)
async def tts_test(
    payload: TTSRequest,
    db: Session = Depends(get_db_dep),  # no lo usamos, pero mantiene la firma consistente
):
    if not settings.ELEVENLABS_API_KEY or not settings.ELEVENLABS_VOICE_ID:
        raise HTTPException(
            status_code=400,
            detail="ElevenLabs no está configurado. Revisa ELEVENLABS_API_KEY y ELEVENLABS_VOICE_ID en el .env",
        )

    audio_url = await tts_generate_audio_url(payload.text)
    if not audio_url:
        raise HTTPException(
            status_code=500,
            detail="Falló la generación de audio con ElevenLabs. Revisa logs del servidor.",
        )

    return TTSResponse(audio_url=audio_url)
