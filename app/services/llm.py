from typing import Any, Dict, List
import openai
from app.core.config import settings

openai.api_key = settings.LLM_API_KEY


SYSTEM_PROMPT_GENERAL = """
Eres Arnold, un coach de fitness directo pero motivador, que habla de forma cercana y clara.
Tu tarea es ayudar al usuario con:
- qué entrenar hoy,
- alimentación,
- recuperación,
- sugerencias generales.

Responde de forma corta y accionable, en español, usando un tono amistoso tipo entrenador de gym.
No inventes datos médicos. Si te preguntan algo médico complejo, recomienda consultar a un profesional.
"""

SYSTEM_PROMPT_SESSION = """
Eres Arnold, un coach de fitness que está guiando una sesión de entrenamiento EN TIEMPO REAL.
El usuario te cuenta cómo le fue en las series (pesado, fácil, dolor, cansancio).
Tú debes:
- darle feedback corto,
- motivarlo,
- sugerir cambios sencillos a la siguiente serie (por ejemplo: bajar un poco el peso, subir reps, ajustar técnica).
No des planes completos aquí, solo micro-ajustes y motivación para la siguiente serie.
Siempre responde en español.
"""


async def generate_arnold_response(
    messages: List[Dict[str, str]],
    mode: str = "general",
) -> str:
    """
    messages: lista tipo [{"role": "user"/"assistant"/"system", "content": "..."}]
    mode: 'general' o 'session' para cambiar el tono.
    """

    system_prompt = SYSTEM_PROMPT_GENERAL if mode == "general" else SYSTEM_PROMPT_SESSION

    # Adaptado a openai>=1.0, pero simple
    client = openai.OpenAI(api_key=settings.LLM_API_KEY)

    chat_messages = [{"role": "system", "content": system_prompt}] + messages

    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=chat_messages,  # type: ignore
        temperature=0.7,
        max_tokens=200,
    )
    return resp.choices[0].message.content or "No tengo una buena respuesta ahora mismo."
