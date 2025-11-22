from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
import enum


class ChatType(str, enum.Enum):
    GENERAL = "general"
    SESSION = "session"


class SessionStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    goal = Column(String, nullable=True)  # "hypertrophy", "fat_loss", etc.
    experience_level = Column(String, nullable=True)  # "beginner", "intermediate", "advanced"

    # metricas básicas
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)

    sessions = relationship("WorkoutSession", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    muscle_group = Column(String, nullable=False)  # "chest", "legs", "back", etc.
    equipment = Column(String, nullable=True)  # "barbell", "dumbbell", etc.
    level = Column(String, nullable=True)  # "beginner", "advanced"

    sets = relationship("WorkoutSet", back_populates="exercise")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.PLANNED)

    # contexto de recuperación
    fatigue_before = Column(Float, nullable=True)  # 1-10
    sleep_hours_last_night = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="sessions")
    sets = relationship("WorkoutSet", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="session")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    exercise_order = Column(Integer, nullable=False, default=0)
    set_number = Column(Integer, nullable=False, default=1)

    # objetivo planificado
    target_reps = Column(Integer, nullable=False)
    target_weight = Column(Float, nullable=True)  # kg, nullable para bodyweight

    # resultado real
    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    rpe = Column(Float, nullable=True)  # 1-10
    comment = Column(Text, nullable=True)

    # flag para saber si fue ajustado por Arnold
    auto_adjusted = Column(Boolean, default=False)

    session = relationship("WorkoutSession", back_populates="sets")
    exercise = relationship("Exercise", back_populates="sets")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=True)
    chat_type = Column(Enum(ChatType), nullable=False)
    role = Column(String, nullable=False)  # "user" | "arnold"

    text = Column(Text, nullable=False)
    audio_url = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")
    session = relationship("WorkoutSession", back_populates="messages")
