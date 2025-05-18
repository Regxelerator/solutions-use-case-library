from utils import state

from utils import constants as C
from audio.recorder import recorder
from workers.transcript_updater import transcript_updater
from workers.commentator import commentator_worker
from ui.popup import popup
import asyncio, signal


async def main():
    popup("", "")                                
    asyncio.create_task(transcript_updater())    
    asyncio.create_task(commentator_worker())    
    await recorder()                             

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda *_: asyncio.get_event_loop().stop())
    asyncio.run(main())
