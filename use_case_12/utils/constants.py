from __future__ import annotations
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

WS_URL   = "wss://api.openai.com/v1/realtime?intent=transcription"
MODEL_RT = "gpt-4o-transcribe"
MODEL_CM = "gpt-4.1"

_vector_env = os.getenv("VECTOR_STORE_IDS")
if not _vector_env:
    raise RuntimeError("Please set VECTOR_STORE_IDS in your .env file")

VECTOR_STORE_IDS = [v.strip() for v in _vector_env.split(",") if v.strip()]

COMMENT_INTERVAL   = 60   
TRANSCRIPT_REFRESH = 5    

RATE  = 24_000
CHUNK = 1024
CHANS = 1

OUT_PATH = pathlib.Path("transcript_live.json")
