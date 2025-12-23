import asyncio
import json
import websockets
from utils.call_session import CallSession
from utils.globals import AUTH_TOKEN

# --- Websocket Audio Bot --- #

async def listen_chat(call_session: CallSession):
    ws_url = f"wss://ai.arkami.org/api/chats/{call_session.chat_id}/messages/subscribe"

    async with websockets.connect(
        ws_url,
        additional_headers=[
            ("Authorization", f"Bearer {AUTH_TOKEN}"),
            ("Cookie", f"auth-token-user={AUTH_TOKEN}")
        ]
    ) as websocket:
        print(f"[Chat] Connected to chat {call_session.chat_id}")

        while not call_session.stop_event.is_set():
            try:
                msg = await asyncio.wait_for(websocket.recv(), None)
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                break

            data = json.loads(msg)

            messages = data.get("messages", [])
            if not messages:
                continue

            last_msg = messages[-1]

            if last_msg.get("sender") != "assistant":
                continue
            
            if last_msg.get("status") != "ready":
                continue

            call_session.file_url_message = last_msg.get("audio_file_url")
            call_session.assistant_audio_ready.set()

    print("[Chat] Chat listener stopped")