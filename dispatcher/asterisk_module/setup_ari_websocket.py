import io
import json
import asyncio
import websockets
from utils.call_session import CallSession
from utils.session_manager import SessionManager
from utils.globals import (
    ACTIVE_CALLS, 
    RECORDING_NAME, 
    ARKAMI_ROOT_URL,
    CALL_SEMAPHORE,
    ARI_WEBSOCKET_URL,
)
from asterisk_module.ari_funcs import (
    record_channel, 
    stop_record_and_save,
    get_recording, 
    playback_recording,
    stop_playback
)
from audio_bot_module.audio_bot_funcs import (
    send_audio_to_chatbot,
    create_chat_with_chatbot
)
from audio_bot_module.setup_audio_bot_websocket import listen_chat

# --- ARI WebSocket listener ---
async def listen_ari(session_manager: SessionManager):
    async with websockets.connect(ARI_WEBSOCKET_URL) as ws:
        print("[ARI] Connected to ARI WebSocket")
        try:
            while True:
                raw = await ws.recv()
                event = json.loads(raw)
                event_type = event.get("type")

                if event_type == "ChannelTalkingStarted":
                    await customer_is_speaking(event, session_manager)

                if event_type == "ChannelTalkingFinished":
                    await customer_stopped_speaking(event, session_manager)

                if event_type == "StasisStart":
                    await CALL_SEMAPHORE.acquire()
                    await on_stasis_start(event, session_manager)

                elif event_type == "RecordingFinished":
                    await on_recording_finished(event, session_manager)

                elif event_type == "PlaybackFinished":
                    await on_playback_finished(event)

                elif event_type == "StasisEnd":
                    CALL_SEMAPHORE.release()
                    await on_stasis_end(event)
                    
        except websockets.exceptions.ConnectionClosed:
            print("[ARI] WebSocket closed")
        except Exception as e:
            print(f"[ARI] Error: {e}")

async def customer_stopped_speaking(event, session_manager: SessionManager):
    channel_id = event["channel"]["id"]
    call = ACTIVE_CALLS.get(channel_id)

    if not call:
        return

    if not call.is_recording:
        return
    
    call.is_recording = False
    recording_name = f"{RECORDING_NAME}_{channel_id}"
    await stop_record_and_save(recording_name, session_manager.get_ari_session())

async def customer_is_speaking(event, session_manager: SessionManager):
    channel_id = event["channel"]["id"]
    call = ACTIVE_CALLS.get(channel_id)

    if not call:
        return

    if call.is_recording:
        return

    if call.playback_id:
        await stop_playback(call.playback_id, session_manager.get_ari_session())
    
    call.is_recording = True
    await record_channel(channel_id, session_manager.get_ari_session())

async def on_stasis_start(event: dict, session_manager: SessionManager):
    channel_id = event["channel"]["id"]
    print(f"[ARI] Call initialized for {channel_id}")

    chat_id = await create_chat_with_chatbot(session_manager.get_chat_session())

    call_session = CallSession(channel_id, chat_id)

    call_session.stop_event = asyncio.Event()
    call_session.chat_task = asyncio.create_task(
        listen_chat(call_session)
    )

    ACTIVE_CALLS[channel_id] = call_session


async def on_recording_finished(event: dict, session_manager: SessionManager):
    channel_id = str(event["recording"]["target_uri"]).split(":")[-1].strip()

    recording_name = f"{RECORDING_NAME}_{channel_id}"

    file_bytes = await get_recording(recording_name, session_manager.get_ari_session())
    file_obj = io.BytesIO(file_bytes)

    call: CallSession = ACTIVE_CALLS.get(channel_id) # type: ignore

    if not call:
        print("Error getting call information")
        return
    
    await send_audio_to_chatbot(file_obj, call.chat_id, session_manager.get_chat_session())

    print("[ARI] Waiting for assistant reply from WebSocket...")
    await call.assistant_audio_ready.wait() 

    call.assistant_audio_ready.clear()

    playback_url =  f"{ARKAMI_ROOT_URL}{call.file_url_message}"

    # ---- Play audio ----
    playback_id = await playback_recording(channel_id, playback_url, session_manager.get_ari_session())
    call.playback_id = playback_id

async def on_playback_finished(event):
    print("[ARI] Playback finished. Listening again...")


async def on_stasis_end(event: dict):
    channel_id = event["channel"]["id"]
    print(f"[ARI] Channel left Stasis {channel_id}")

    call = ACTIVE_CALLS.pop(channel_id, None)
    if not call:
        return
    
    if not call.chat_task:
        return

    call.stop_event.set()
    call.chat_task.cancel()

    try:
        await call.chat_task
    except asyncio.CancelledError:
        pass
    
    print("[ARI] Cleaned up call state")