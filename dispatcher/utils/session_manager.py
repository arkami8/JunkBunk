import aiohttp
from utils.globals import ARI_PASS, ARI_USER, AUTH_TOKEN


class SessionManager():
    def __init__(self):
        self.ari_session: aiohttp.ClientSession
        self.chat_session: aiohttp.ClientSession

    async def initialize_sessions(self):
        self.ari_session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(ARI_USER, ARI_PASS)
        )

        self.chat_session = aiohttp.ClientSession(
            headers={
                "authorization": f"Bearer {AUTH_TOKEN}",
                "cookie": f"auth-token-user={AUTH_TOKEN}",
            }
        )

    async def cleanup_sessions(self):
        await self.ari_session.close()
        await self.chat_session.close()

    def get_ari_session(self):
        return self.ari_session

    def get_chat_session(self):
        return self.chat_session