import io
import aiohttp
from aiohttp import ClientSession
from utils.globals import AUTH_TOKEN, CONNECT_CHATBOT_URL, API_CHATBOT_URL, BOT_NAME

async def create_chat_with_chatbot(chat_session: ClientSession) -> str:
    """
    Async version of sending a request to create a chat with the chatbot.
    """
    data = {"chatbot_slug": BOT_NAME}

    headers = {
        "authorization": f"Bearer {AUTH_TOKEN}",
        "cookie": f"auth-token-user={AUTH_TOKEN}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    async with chat_session.post(CONNECT_CHATBOT_URL, json=data, headers=headers) as resp:
        text = await resp.text()
        try:
            result = await resp.json()
        except Exception:
            print("Response is not JSON:", text)
            raise

        return result["chat_id"]

async def send_audio_to_chatbot(file_bytes: io.BytesIO, chat_id: str, chat_session: ClientSession):
    headers = {
        "authorization": f"Bearer {AUTH_TOKEN}",
        "cookie": f"auth-token-user={AUTH_TOKEN}",
        "accept": "application/json"
    }

    data = {"chat_id": chat_id, "chatbot_slug": BOT_NAME}

    form = aiohttp.FormData()
    for key, value in data.items():
        form.add_field(key, value)
    form.add_field("file", file_bytes, filename="audio.wav", content_type="audio/wav")

    async with chat_session.post(API_CHATBOT_URL, data=form, headers=headers) as resp:
        result = await resp.json()
        print("[CHATBOT] Message sent:", result)