import uuid
import os
from typing import Optional
import httpx

from app.core.config import settings


async def tts_generate_audio_url(text: str) -> Optional[str]:
    """
    Llama a ElevenLabs para generar un MP3 con la respuesta de Arnold.
    - Si no hay API key o voice_id configurados, devuelve None.
    - Si falla la llamada a ElevenLabs, devuelve None (para no romper el flujo del chat).
    - Si funciona, guarda el audio en MEDIA_DIR y devuelve la URL relativa (/media/xxx.mp3).
    """
    if not settings.ELEVENLABS_API_KEY or not settings.ELEVENLABS_VOICE_ID:
        # No está configurado ElevenLabs, seguimos solo con texto
        return None

    # Endpoint oficial TTS HTTP (no streaming)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            audio_bytes = resp.content
    except Exception as e:
        # Puedes loguear si quieres
        print(f"[ElevenLabs] Error generando audio: {e}")
        return None

    # Guardar audio en disco
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(settings.MEDIA_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    # URL que el front puede usar: BASE_URL + audio_url
    return f"/media/{filename}"
