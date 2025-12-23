import asyncio

class CallSession:
    def __init__(self, channel_id: str, chat_id: str):
        self.channel_id = channel_id
        self.chat_id = chat_id

        self.assistant_audio_ready = asyncio.Event()
        self.file_url_message: str | None = None
        self.stop_event = asyncio.Event()
        self.chat_task: asyncio.Task | None = None
        self.is_recording: bool = False
        self.playback_id: str | None = None

        # unused for now
        self.is_talking_to_user: bool = False