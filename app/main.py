import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import Base, engine
from app.api.routes import chat, sessions, setup, tts
from fastapi.middleware.cors import CORSMiddleware

# 👉 Esto crea todas las tablas en la BD
Base.metadata.create_all(bind=engine)

# Crear carpeta media si no existe
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
origins = [
    "http://localhost:19006",  # Expo web
    "http://localhost:8081",
    "http://127.0.0.1:19006",
    # añade aquí la IP de tu máquina en la red local si pruebas en dispositivo físico
    "*"
]

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Arnold Coach API is running"}


app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(setup.router)
app.include_router(tts.router)