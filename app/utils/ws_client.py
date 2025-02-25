import json
import logging
import websockets
from typing import Annotated
from fastapi import Depends, HTTPException

from app.core.config import settings


log = logging.getLogger("uvicorn")
log.setLevel(logging.DEBUG if settings.debug else logging.INFO)


class AuthWebSocketClient:
    def __init__(self):
        self.auth_ws_url = f"ws://{settings.AUTH_URL}/ws"
        self.headers = {"X-Internal-Key": settings.INTERNAL_KEY}
        self.connection = None

    async def connect(self):
        if not self.connection or self.connection.closed:
            try:
                # Add INTERNAL_KEY as a custom header
                self.connection = await websockets.connect(self.auth_ws_url, extra_headers=self.headers)
                log.info("Connected to Auth service WebSocket.")
            except Exception as e:
                log.info(f"Failed to connect to Auth service: {e}")
                raise HTTPException(status_code=503, detail="Auth service is unavailable")

    async def send(self, action: str, content: dict) -> dict:
        """
        Actions supporting: 'auth_bot' and 'validate'
        """
        await self.connect()
        request = {"action": action, "content": content}
        await self.connection.send(json.dumps(request))
        log.debug(f"Sent: {request}")

        response = await self.connection.recv()
        log.debug(f"Received: {response}")
        return json.loads(response)

    async def close(self):
        if self.connection:
            await self.connection.close()
            log.info("WebSocket connection closed.")


# FastAPI dependency
async def get_auth_ws_client():
    client = AuthWebSocketClient()
    try:
        await client.connect()
        yield client
    finally:
        await client.close()


AuthWSClient = Annotated[AuthWebSocketClient, Depends(get_auth_ws_client)]
