import asyncio
from utils.call_session import CallSession

ARI_USER = "chatbot"
ARI_PASS = "YoPhoneLinging"
ARI_URL = "http://localhost:8088/ari"
API_CHATBOT_URL = "https://ai.arkami.org/api/messages-audio"
CONNECT_CHATBOT_URL = "https://ai.arkami.org/api/chats"
ARKAMI_ROOT_URL = "https://ai.arkami.org/"
ARI_WEBSOCKET_URL = f"ws://localhost:8088/ari/events?api_key={ARI_USER}:{ARI_PASS}&app=chatbot"


ACTIVE_CALLS: dict[str, CallSession] = {}
AUTH_TOKEN = "HYoUMLwL6Mkp5RsxyNggLH712fBRu8KV04t2G63f717252312"
RECORDING_NAME = "user_recording"
RECORDING_FORMAT = "wav"

MAX_CALLS = 50
CALL_SEMAPHORE = asyncio.Semaphore(MAX_CALLS)


