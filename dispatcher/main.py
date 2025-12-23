import asyncio
from utils.session_manager import SessionManager
from asterisk_module.setup_ari_websocket import listen_ari

async def main():
    session_manager: SessionManager = SessionManager()
    await session_manager.initialize_sessions()

    try:
        await asyncio.gather(
            listen_ari(session_manager)
        )
    except Exception as e:
        print(e)
        await session_manager.cleanup_sessions()
    finally:
        await session_manager.cleanup_sessions()

if __name__ == "__main__":
    asyncio.run(main())
