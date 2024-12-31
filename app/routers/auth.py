from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import DBSession
from app.utils.auth import authenticate_user, create_access_token


router = APIRouter(prefix="/auth")

OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token")
def login(form_data: OAuthForm, session: DBSession):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
