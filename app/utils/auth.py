import requests
from typing import Annotated
from json import JSONDecodeError
from fastapi import Request, HTTPException, status, Depends

from app.models.users import User
from app.core.config import settings


AUTH_BASE_URL = settings.auth_base_url
TOKEN_VERIFY_URL = f"{AUTH_BASE_URL}/auth/verify/"


def authenticate(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheme")

    token = auth_header.split(" ", 1)[1]
    response = requests.post(TOKEN_VERIFY_URL, json={"token": token})
    if response.status_code == status.HTTP_200_OK:
        try:
            user_data = response.json()
            return User(**user_data)
        except JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    raise HTTPException(status_code=response.status_code, detail="Authentication error")


CurrentUser = Annotated[User, Depends(authenticate)]
