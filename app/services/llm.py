from typing import Any, Dict


async def generate_arnold_response(
    messages: list[Dict[str, str]],
    mode: str = "general",
) -> str:
    """
    Stub: acá se conectaría al LLM real.
    `messages` es una lista tipo [{"role": "user"/"assistant"/"system", "content": "..."}]
    `mode` puede ser "general" o "session" para cambiar el prompt.
    """
    # Para MVP sin LLM todavía, devolvemos algo dummy
    if mode == "general":
        return "Hoy te recomiendo entrenar pecho y tríceps. ¿Quieres que te arme una rutina?"
    else:
        return "Buen trabajo en esa serie. Bajemos un poco el peso para la siguiente y concéntrate en la técnica."
