import requests
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

AUTH_BASE_URL = settings.auth_base_url
TOKEN_VERIFY_URL = f"{AUTH_BASE_URL}/verify"


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")

        if not token:
            raise HTTPException(status_code=401, detail="Authorization token is missing")

        token = token.split("Bearer ")[-1]

        response = requests.request("POST", TOKEN_VERIFY_URL, data={"token": token}).json()
        user_id = response.get("uid")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Attach user_id to the request state so it can be accessed later
        request.state.user_id = user_id

        response = await call_next(request)
        return response
