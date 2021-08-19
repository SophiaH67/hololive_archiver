from hololive import hololive
from streams import Stream, StreamAlreadyExists
import asyncio
import re
import sys
from config import add_stream, topics, locations

async def update_scheduled_streams():
    for topic in topics:
        streams = await hololive.get_live(topic=topic, limit=50)
        print(len(streams))
        for stream in streams:
            try:
                add_stream(Stream(stream.title, stream.id, stream.available_at, True, True, output_override=f"{locations['final']}/{topic}/"))
            except StreamAlreadyExists:
                continue
            print("[AUTOSCHEDULER] {} is a wanted {} stream. Planning to archive it!".format(stream.title, topic))

async def periodic_updates():
    while True:
        await update_scheduled_streams()
        await asyncio.sleep(30)

try:
    asyncio.run(periodic_updates())
except KeyboardInterrupt:
    sys.exit(0)