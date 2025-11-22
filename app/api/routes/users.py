from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user_profile(user_id: int, db: Session = Depends(get_db_dep)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "experience_level": user.experience_level,
        "goal": user.goal,
    }
