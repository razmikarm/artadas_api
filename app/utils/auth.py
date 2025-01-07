import requests
from uuid import UUID
from typing import Annotated
from sqlmodel import SQLModel
from json import JSONDecodeError
from fastapi import Request, HTTPException, status, Depends

from app.core.config import settings


AUTH_BASE_URL = settings.auth_base_url
TOKEN_VERIFY_URL = f"{AUTH_BASE_URL}/auth/verify/"


class User(SQLModel):
    id: UUID
    username: str
    email: str
    full_name: str


def authenticate(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scheme")

    response = requests.post(TOKEN_VERIFY_URL, {"token": token})
    # Ensure the request was successful
    print("* " * 20, response.text, sep="\n")
    if response.status_code == 200:
        try:
            user_data = response.json()
            return User(**user_data)
        except JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


CurrentUser = Annotated[User, Depends(authenticate)]
