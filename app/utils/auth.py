import json
from typing import Annotated
from redis.asyncio import Redis
from fastapi import Request, HTTPException, status, Depends

from app.models.users import User
from app.core.config import settings
from app.utils.ws_client import AuthWSClient


class Auth:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)

    async def validate(self, token: str, ws_client: AuthWSClient) -> str:
        redis_key = f"access_token:{token}"
        user_data = await self.redis.get(redis_key)
        if user_data:
            return User(**json.loads(user_data))
        # If token not found in Redis, fetch from Auth service via WebSocket
        response = ws_client.send(action="validate", content={"token": token})
        response_data = json.loads(response)
        if response_data.get("status") != "ok":
            return HTTPException(response_data["message"])
        user_data = await self.redis.get(redis_key)
        user = User(**json.loads(user_data))
        return user

    async def auth_bot(self, tg_user_data: dict, ws_client: AuthWSClient) -> str:
        tg_user_id = tg_user_data["id"]
        redis_key = f"tg_token:{tg_user_id}"
        user_data = await self.redis.get(redis_key)
        if user_data:
            return User(**json.loads(user_data))
        # If token not found in Redis, fetch from Auth service via WebSocket
        response = ws_client.send(action="validate", content=tg_user_data)
        response_data = json.loads(response)
        if response_data.get("status") != "ok":
            return HTTPException(response_data["message"])
        user_data = await self.redis.get(redis_key)
        return User(**json.loads(user_data))


async def check_token_validation(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheme")

    token = auth_header.split(" ", 1)[1]
    return Auth().validate(token)


CurrentUser = Annotated[User, Depends(check_token_validation)]
