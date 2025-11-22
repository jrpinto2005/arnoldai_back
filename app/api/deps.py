from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db


def get_db_dep(db: Session = Depends(get_db)):
    return db
