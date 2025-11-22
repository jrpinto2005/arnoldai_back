from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    fitness_goal = Column(String, nullable=True)  # weight_loss, muscle_gain, etc.
    activity_level = Column(String, nullable=True)  # sedentary, active, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    workout_type = Column(String, nullable=True)  # strength, cardio, flexibility, etc.
    duration_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Float, nullable=True)
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    status = Column(String, default="planned")  # planned, in_progress, completed, cancelled
    scheduled_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workout_sessions")
    exercises = relationship("Exercise", back_populates="workout_session")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    name = Column(String, nullable=False)
    exercise_type = Column(String, nullable=True)  # strength, cardio, etc.
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # in kg
    duration_seconds = Column(Integer, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    order_in_workout = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercises")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_name = Column(String, nullable=True)
    session_type = Column(String, default="general")  # general, workout_planning, nutrition, motivation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    message_type = Column(String, default="text")  # text, audio, image
    audio_url = Column(String, nullable=True)  # For voice messages
    metadata = Column(Text, nullable=True)  # JSON metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
