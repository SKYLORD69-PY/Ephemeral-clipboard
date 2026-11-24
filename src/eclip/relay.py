import asyncio
import json
import secrets
import time
from dataclasses import dataclass, field

import websockets
from websockets.asyncio.server import ServerConnection


@dataclass
class Room:
    sender: ServerConnection
    created_at: float = field(default_factory=time.monotonic)
    receiver: ServerConnection | None = None


class Relay:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.rooms: dict[str, Room] = {}
        self.connections: dict[ServerConnection, str] = {}
        self.ttl_seconds = ttl_seconds

    def _claim_nameplate(self) -> str:
        for _ in range(1000):
            nameplate = f"{secrets.randbelow(1000):03d}"
            if nameplate not in self.rooms:
                return nameplate
        raise RuntimeError("No free nameplates")

    async def _close_room(self, nameplate: str) -> None:
        room = self.rooms.pop(nameplate, None)
        if room is None:
            return

        self.connections.pop(room.sender, None)
        if room.receiver is not None:
            self.connections.pop(room.receiver, None)
        await room.sender.close(code=1000, reason="room deleted")
        if room.receiver is not None:
            await room.receiver.close(code=1000, reason="room deleted")

    async def close(self, websocket: ServerConnection) -> None:
        nameplate = self.connections.pop(websocket, None)
        if nameplate is not None:
            await self._close_room(nameplate)

    async def handler(self, websocket: ServerConnection) -> None:
        try:
            async for raw in websocket:
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"type": "error", "error": "invalid json"}))
                    continue

                action = message.get("action")

                if action == "claim":
                    nameplate = self._claim_nameplate()
                    room = Room(sender=websocket)
                    self.rooms[nameplate] = room
                    self.connections[websocket] = nameplate
                    await websocket.send(
                        json.dumps({"type": "claimed", "nameplate": nameplate})
                    )
                    continue

                if action == "join":
                    nameplate = message.get("nameplate")
                    joined_room = self.rooms.get(nameplate)
                    if joined_room is None:
                        await websocket.send(
                            json.dumps({"type": "error", "error": "room not found"})
                        )
                        continue
                    if joined_room.receiver is not None:
                        await websocket.send(
                            json.dumps({"type": "error", "error": "room full"})
                        )
                        continue

                    joined_room.receiver = websocket
                    self.connections[websocket] = nameplate
                    await websocket.send(json.dumps({"type": "joined"}))
                    await joined_room.sender.send(
                        json.dumps({"type": "receiver-ready"})
                    )
                    continue

                if action == "message":
                    nameplate = message.get("nameplate")
                    member_nameplate = self.connections.get(websocket)
                    if nameplate is not None and nameplate != member_nameplate:
                        await websocket.send(
                            json.dumps({"type": "error", "error": "not in room"})
                        )
                        continue
                    if member_nameplate is None:
                        await websocket.send(
                            json.dumps({"type": "error", "error": "not in room"})
                        )
                        continue

                    message_room = self.rooms.get(member_nameplate)
                    if message_room is None:
                        await websocket.send(
                            json.dumps({"type": "error", "error": "room not found"})
                        )
                        continue
                    if (
                        websocket is not message_room.sender
                        and websocket is not message_room.receiver
                    ):
                        await websocket.send(
                            json.dumps({"type": "error", "error": "not in room"})
                        )
                        continue

                    target = (
                        message_room.receiver
                        if websocket is message_room.sender
                        else message_room.sender
                    )
                    if target is not None:
                        await target.send(
                            json.dumps(
                                {
                                    "type": "message",
                                    "payload": message.get("payload"),
                                    "payloadType": message.get("payloadType"),
                                }
                            )
                        )
                    if message.get("payloadType") == "payload":
                        await self._close_room(member_nameplate)
        finally:
            await self.close(websocket)

    async def reap_expired_rooms(self) -> None:
        while True:
            await asyncio.sleep(10)
            now = time.monotonic()
            expired = [
                nameplate
                for nameplate, room in self.rooms.items()
                if now - room.created_at >= self.ttl_seconds
            ]
            for nameplate in expired:
                await self._close_room(nameplate)


async def serve(host: str = "0.0.0.0", port: int = 8765) -> None:
    relay = Relay()
    async with websockets.serve(relay.handler, host, port):
        reaper = asyncio.create_task(relay.reap_expired_rooms())
        try:
            await asyncio.Future()
        finally:
            reaper.cancel()
