from __future__ import annotations
import asyncio
import queue
from ui.popup import popup
from audio.recorder import comment_queue
from utils.constants import TRANSCRIPT_REFRESH
from utils import state                                 

transcript_turns = state.transcript_turns
all_questions     = state.all_questions


async def transcript_updater(every: int = TRANSCRIPT_REFRESH) -> None:
    while True:
        try:
            while True:
                turn = comment_queue.get_nowait()
                transcript_turns.append(f"[{turn['timestamp']}] {turn['text']}")
        except queue.Empty:
            pass

        if transcript_turns:
            full_tx = "\n".join(transcript_turns)
            qs_text = "\n\n".join(all_questions)        
            popup(full_tx, qs_text)

        await asyncio.sleep(every)