from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db import User, get_db

router = APIRouter()


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form.username))
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if user is None:
        raise invalid

    valid, new_hash = verify_password(form.password, user.hashed_password)
    if not valid:
        raise invalid

    if new_hash:  # bcrypt -> argon2 upgrade, persist it
        user.hashed_password = new_hash
        db.commit()

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
