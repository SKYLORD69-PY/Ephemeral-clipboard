import json

import pytest
import websockets

from eclip.relay import Relay


@pytest.mark.asyncio
async def test_payload_delivered_once_and_room_deleted() -> None:
    relay = Relay(ttl_seconds=300)
    async with websockets.serve(relay.handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]

        async with websockets.connect(f"ws://127.0.0.1:{port}") as sender:
            await sender.send(json.dumps({"action": "claim"}))
            claimed = json.loads(await sender.recv())
            nameplate = claimed["nameplate"]

            async with websockets.connect(f"ws://127.0.0.1:{port}") as receiver:
                await receiver.send(
                    json.dumps({"action": "join", "nameplate": nameplate})
                )
                assert json.loads(await receiver.recv())["type"] == "joined"
                assert json.loads(await sender.recv())["type"] == "receiver-ready"

                await sender.send(
                    json.dumps(
                        {
                            "action": "message",
                            "nameplate": nameplate,
                            "payload": "encrypted-demo",
                            "payloadType": "payload",
                        }
                    )
                )
                delivered = json.loads(await receiver.recv())
                assert delivered["payload"] == "encrypted-demo"
                assert nameplate not in relay.rooms

                await receiver.send(
                    json.dumps({"action": "join", "nameplate": nameplate})
                )
                failed = json.loads(await receiver.recv())
                assert failed["error"] == "room not found"


@pytest.mark.asyncio
async def test_third_client_is_room_full() -> None:
    relay = Relay()
    async with websockets.serve(relay.handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]

        async with websockets.connect(f"ws://127.0.0.1:{port}") as sender:
            await sender.send(json.dumps({"action": "claim"}))
            nameplate = json.loads(await sender.recv())["nameplate"]

            async with websockets.connect(f"ws://127.0.0.1:{port}") as receiver:
                await receiver.send(
                    json.dumps({"action": "join", "nameplate": nameplate})
                )
                await receiver.recv()
                await sender.recv()

                async with websockets.connect(
                    f"ws://127.0.0.1:{port}"
                ) as third:
                    await third.send(
                        json.dumps({"action": "join", "nameplate": nameplate})
                    )
                    response = json.loads(await third.recv())
                    assert response["error"] == "room full"


@pytest.mark.asyncio
async def test_outside_connection_cannot_forward_or_delete() -> None:
    relay = Relay()
    async with websockets.serve(relay.handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]

        async with websockets.connect(f"ws://127.0.0.1:{port}") as sender:
            await sender.send(json.dumps({"action": "claim"}))
            nameplate = json.loads(await sender.recv())["nameplate"]

            async with websockets.connect(f"ws://127.0.0.1:{port}") as outsider:
                await outsider.send(
                    json.dumps(
                        {
                            "action": "message",
                            "nameplate": nameplate,
                            "payload": "attempt",
                            "payloadType": "payload",
                        }
                    )
                )
                response = json.loads(await outsider.recv())
                assert response["error"] == "not in room"
                assert nameplate in relay.rooms
