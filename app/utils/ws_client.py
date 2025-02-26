import json
import logging
import asyncio
from websockets import connect, ConnectionClosed
from typing import Literal, Annotated
from fastapi import Depends, HTTPException

from app.core.config import settings


log = logging.getLogger("uvicorn")
log.setLevel(logging.DEBUG if settings.debug else logging.INFO)


class AuthWebSocketClient:
    def __init__(self, URI: str):
        self.uri = URI
        self.headers = {"X-Internal-Key": settings.INTERNAL_API_KEY}
        self.connection = None

    async def _connect(self):
        if self.connection:
            return
        try:
            self.connection = await connect(self.uri, additional_headers=self.headers)
            log.info("Connected to Auth service via WebSocket.")
        except Exception as e:
            log.info(f"Failed to connect to Auth service: {e}")
            log.debug(f"Auth serice URL: {settings.AUTH_WS_URL}")
            log.debug(f"INTERNAL KEY: {settings.INTERNAL_API_KEY}")
            raise HTTPException(status_code=503, detail="Authentication is not available")

    async def send(self, action: Literal["auth_bot", "validate"], content: dict) -> dict:
        await self._connect()
        request = {"action": action, "content": content}
        await self.connection.send(json.dumps(request))
        log.debug(f"Sent: {request}")
        response = await self.connection.recv()
        log.debug(f"Received: {response}")
        return json.loads(response)

    @property
    async def is_closed(self):
        try:
            self.connection.ping()
            return False
        except ConnectionClosed:
            return True

    async def close(self):
        if not self.connection:
            return
        await self.connection.close()
        log.debug("WebSocket connection closed.")
        self.connection = None


class WebSocketPool:
    def __init__(self):
        log.debug("Creating Web Socket Pool...")
        self.uri = settings.AUTH_WS_URL
        self.pool = asyncio.Queue(settings.WS_POOL_SIZE)
        self.lock = asyncio.Lock()
        log.debug("Created Web Socket Pool.")

    async def _get_or_return_connection(
        self, websocket: AuthWebSocketClient | None = None
    ) -> AuthWebSocketClient | None:
        # async with self.lock:
        if not websocket:
            log.debug("Asking for a WS connection...")
            if self.pool.empty():
                log.debug("Creating WS connection...")
                websocket = AuthWebSocketClient(self.uri)
                await self.pool.put(websocket)
                log.debug("Created new WS connection.")
            return await self.pool.get()
        if not await websocket.is_closed:
            self.pool.put(websocket)
            return
        log.warning("Websocket client is closed")

    async def send(self, **data: dict) -> dict:
        """Send data safely using the lock."""
        conn = await self._get_or_return_connection()
        response = await conn.send(**data)
        await self._get_or_return_connection(conn)
        return response

    async def close_all(self):
        """Close all connections."""
        log.debug("Closing all WS connection in the pool.")
        while not self.pool.empty():
            conn = await self.pool.get()
            await conn.close()


# Initialize a pool
ws_pool = WebSocketPool()


# FastAPI dependency
async def get_auth_ws_pool():
    return ws_pool


AuthWSClient = Annotated[AuthWebSocketClient, Depends(get_auth_ws_pool)]
