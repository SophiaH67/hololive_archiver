from hololive import hololive
from streams import Stream
import asyncio
import re
import sys
from config import add_stream, categories

async def update_scheduled_streams():
    streams = await hololive.get_streams()
    for stream in streams:
        category = ""
        video_id = stream.url.split('?v=')[1]
        for cat in categories:
            for word in categories[cat]:
                if re.search(word, stream.title_jp, re.IGNORECASE):
                    category = cat
        if category == "":
            try:
                add_stream(Stream(stream.title_jp, video_id, stream.starttime, True, False))
            finally:
                continue
        try:
            add_stream(Stream(stream.title_jp, video_id, stream.starttime, True, True))
        except:
            continue
        print("[AUTOSCHEDULER] {} is a wanted {} stream. Planning to archive it!".format(stream.title_jp, category))

async def periodic_updates():
    while True:
        await update_scheduled_streams()
        await asyncio.sleep(30)

try:
    asyncio.run(periodic_updates())
except KeyboardInterrupt:
    sys.exit(0)