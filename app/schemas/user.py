from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    goal: str | None = None
    experience_level: str | None = None
    weight_kg: float | None = None
    height_cm: float | None = None


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
