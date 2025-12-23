from aiohttp import ClientSession
from utils.globals import ARI_URL, RECORDING_FORMAT, RECORDING_NAME

async def record_channel(channel_id, ari_session: ClientSession):
    recording_name = f"{RECORDING_NAME}_{channel_id}"
    params = {
        "name": recording_name,
        "format": RECORDING_FORMAT,
        "ifExists": "overwrite",
    }
    print(f"[ARI] Recording started on {channel_id}")
    await ari_session.post(f"{ARI_URL}/channels/{channel_id}/record", params=params)

async def stop_record_and_save(recording_name, ari_session: ClientSession):
    await ari_session.post(f"{ARI_URL}/recordings/live/{recording_name}/stop")
    print(f"[ARI] Recording stopped")

async def get_recording_ari_13(recording_name, ari_session: ClientSession):
    resp = await ari_session.get(
        f"{ARI_URL}/recordings/stored/{recording_name}"
    )

    if resp.status != 200:
        text = await resp.text()
        raise Exception(f"Failed to fetch recording: {resp.status}, {text}")

    file_bin = await resp.read()
    print(f"[ARI] File Received!")

    return file_bin

async def get_recording(recording_name, ari_session: ClientSession):
    resp = await ari_session.get(
        f"{ARI_URL}/recordings/stored/{recording_name}/file"
    )

    if resp.status != 200:
        text = await resp.text()
        raise Exception(f"Failed to fetch recording: {resp.status}, {text}")

    file_bin = await resp.read()
    print(f"[ARI] File Received!")

    return file_bin

async def playback_recording(channel_id, full_path, ari_session: ClientSession):
    media = f"sound:{full_path}"

    resp = await ari_session.post(
        f"{ARI_URL}/channels/{channel_id}/play",
        params={"media": media}
    )
    print(f"[ARI] Playing file on {channel_id} -> {full_path}")
    location = resp.headers.get("Location")
    if location:
        playback_id = location.split("/")[-1]
        return playback_id

    print("error getting playback id")
    return

async def stop_playback(playback_id, ari_session: ClientSession):
    await ari_session.delete(f"{ARI_URL}/playbacks/{playback_id}")

# Doesnt exists in asterisk 13. and is comented cuz not used
# async def hangup_channel(channel_id, ari_session: ClientSession):
#     await ari_session.post(f"{ARI_URL}/channels/{channel_id}/hangup")
#     print(f"[ARI] Hung up channel {channel_id}")
