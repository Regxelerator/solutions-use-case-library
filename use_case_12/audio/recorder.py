import os
import json
import base64
import asyncio
import datetime
import pathlib
import queue

import websockets
import pyaudiowpatch as pyaudio
from datetime import timezone


API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Please set OPENAI_API_KEY")

WS_URL   = "wss://api.openai.com/v1/realtime?intent=transcription"
MODEL_RT = "gpt-4o-transcribe"

RATE, CHUNK, CHANS = 24_000, 1024, 1
OUT_PATH = pathlib.Path("transcript_live.json")


comment_queue: "queue.Queue[dict]" = queue.Queue(maxsize=100)


async def recorder() -> None:
    pa = pyaudio.PyAudio()
    mic_idx = pa.get_default_input_device_info()["index"]
    mic_stream = pa.open(format=pyaudio.paInt16, channels=CHANS, rate=RATE,
                         input=True, frames_per_buffer=CHUNK,
                         input_device_index=mic_idx)

    f = OUT_PATH.open("w", encoding="utf-8")
    f.write("[\n")
    first = True

    async with websockets.connect(
        WS_URL,
        extra_headers={
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta":  "realtime=v1"
        },
        max_size=2 ** 23
    ) as ws:
        await ws.send(json.dumps({
            "type": "transcription_session.update",
            "session": {
                "input_audio_format":        "pcm16",
                "input_audio_transcription": {"model": MODEL_RT,
                                              "language": "en"},
                "turn_detection":            {"type": "server_vad"},
                "input_audio_noise_reduction": {"type": "far_field"}
            }
        }))

        while True:
            if json.loads(await ws.recv())["type"] == "transcription_session.updated":
                print("[session ready] → Speak (Ctrl-C to stop)…")
                break

        try:
            while True:
                pcm = mic_stream.read(CHUNK, exception_on_overflow=False)
                await ws.send(json.dumps({
                    "type":  "input_audio_buffer.append",
                    "audio": base64.b64encode(pcm).decode()
                }))

                try:
                    while True:
                        ev = json.loads(await asyncio.wait_for(ws.recv(), 0.01))
                        t  = ev.get("type", "")
                        if t.endswith(".delta"):
                            print(ev["delta"], end="", flush=True)
                        elif t.endswith(".completed"):
                            print()
                            entry = {
                                "timestamp": datetime.datetime.now(timezone.utc)
                                             .isoformat(timespec="seconds") + "Z",
                                "text": ev["transcript"]
                            }
                            # append to file
                            if not first:
                                f.write(",\n")
                            json.dump(entry, f, ensure_ascii=False)
                            f.flush()
                            first = False

                            comment_queue.put(entry)

                except asyncio.TimeoutError:
                    pass

        except KeyboardInterrupt:
            print("\n[stopped]")

        finally:
            mic_stream.stop_stream()
            mic_stream.close()
            pa.terminate()
            f.write("\n]\n")
            f.close()
            print(f"Transcript saved to {OUT_PATH.resolve()}")
