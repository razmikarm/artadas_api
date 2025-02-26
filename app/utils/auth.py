import json
import logging
from typing import Annotated
from redis.asyncio import Redis
from fastapi import Request, HTTPException, status, Depends

from app.models.users import User
from app.core.config import settings
from app.utils.ws_client import AuthWSClient


log = logging.getLogger("uvicorn")
log.setLevel(logging.DEBUG if settings.debug else logging.INFO)


class Auth:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)

    async def validate(self, token: str, ws_client: AuthWSClient) -> str:
        redis_key = f"access_token:{token}"
        user_data = await self.redis.get(redis_key)
        if user_data:
            log.debug("Found user Auth data in Redis")
            return User(**json.loads(user_data))
        # If token not found in Redis, fetch from Auth service via WebSocket
        log.debug("No data found in Redis - Requesting Auth service")
        log.debug(f"Redis key: {redis_key}")
        response = await ws_client.send(action="validate", content={"token": token})
        if response.get("status") != "ok":
            raise HTTPException(status_code=401, detail=response["message"])
        user_data = await self.redis.get(redis_key)
        return User(**json.loads(user_data))

    async def auth_bot(self, tg_user_data: dict, ws_client: AuthWSClient) -> str:
        tg_user_id = tg_user_data["id"]
        redis_key = f"tg_token:{tg_user_id}"
        user_data = await self.redis.get(redis_key)
        if user_data:
            log.debug("Found user Auth data in Redis")
            return User(**json.loads(user_data))
        # If token not found in Redis, fetch from Auth service via WebSocket
        log.debug("No data found in Redis - Requesting Auth service")
        log.debug(f"Redis key: {redis_key}")
        response = ws_client.send(action="validate", content=tg_user_data)
        if response.get("status") != "ok":
            raise HTTPException(status_code=401, detail=response["message"])
        user_data = await self.redis.get(redis_key)
        return User(**json.loads(user_data))


async def check_token_validation(request: Request, ws_client: AuthWSClient) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheme")

    token = auth_header.split(" ", 1)[1]
    return await Auth().validate(token, ws_client)


CurrentUser = Annotated[User, Depends(check_token_validation)]
