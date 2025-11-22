import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import Base, engine
from app.api.routes import chat, sessions, setup, tts

# 👉 Esto crea todas las tablas en la BD
Base.metadata.create_all(bind=engine)

# Crear carpeta media si no existe
os.makedirs(settings.MEDIA_DIR, exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/")
def read_root():
    return {"message": "Arnold Coach API is running"}


app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(setup.router)
app.include_router(tts.router)