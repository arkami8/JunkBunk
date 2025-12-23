import asyncio
import os
from dotenv import load_dotenv
from utils.call_session import CallSession

load_dotenv()

ARI_USER = os.getenv("ARI_USER")
ARI_PASS = os.getenv("ARI_PASS")
ARI_URL = os.getenv("ARI_URL")
ARI_BASE_URL = os.getenv("ARI_BASE_URL")
BOT_NAME = os.getenv("BOT_NAME")
ASTERISK_VER = os.getenv("ASTERISK_VER", "22")
ARI_WEBSOCKET_URL = f"ws://{ARI_BASE_URL}/events?api_key={ARI_USER}:{ARI_PASS}&app={ARI_USER}"

API_CHATBOT_URL = "https://ai.arkami.org/api/messages-audio"
CONNECT_CHATBOT_URL = "https://ai.arkami.org/api/chats"
ARKAMI_ROOT_URL = "https://ai.arkami.org/"

ACTIVE_CALLS: dict[str, CallSession] = {}
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
RECORDING_NAME = os.getenv("RECORDING_NAME", "recording")
RECORDING_FORMAT = os.getenv("RECORDING_FORMAT", "wav")

MAX_CALLS = 50
CALL_SEMAPHORE = asyncio.Semaphore(MAX_CALLS)


