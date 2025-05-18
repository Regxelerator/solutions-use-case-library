from __future__ import annotations
import asyncio
import datetime

from llm.llm_engine import ask_follow_up_questions
from ui.popup import popup
from utils.constants import COMMENT_INTERVAL
from utils import state                                

transcript_turns = state.transcript_turns
chat_history      = state.chat_history
all_questions     = state.all_questions


async def commentator_worker(every: int = COMMENT_INTERVAL) -> None:
    while True:
        if transcript_turns:                                    
            full_tx = "\n".join(transcript_turns)

            chat_history.append({"role": "user", "content": full_tx})

            reply, _resp = ask_follow_up_questions(chat_history)

            all_questions.append(reply)
            qs_text = "\n\n".join(all_questions)

            chat_history.append({"role": "assistant", "content": reply})

            popup(full_tx, qs_text)

            ts = datetime.datetime.now(datetime.timezone.utc)\
                                   .isoformat(timespec="seconds") + "Z"
            print(f"\n🗒️  [{ts}] Follow-up questions:\n{reply}\n")

        await asyncio.sleep(every)