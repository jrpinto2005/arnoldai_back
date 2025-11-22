from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    fitness_goal: Optional[str] = None
    activity_level: Optional[str] = None

class User(UserBase):
    id: int
    age: Optional[int]
    height: Optional[float]
    weight: Optional[float]
    fitness_goal: Optional[str]
    activity_level: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    age: Optional[int]
    height: Optional[float]
    weight: Optional[float]
    fitness_goal: Optional[str]
    activity_level: Optional[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
