import time
from hololive import hololive
import threading
import datetime
import asyncio
import re
import sys
import pathlib
import shutil
import yaml
import os
import youtube_dl

class downloads:
    config = {}
    scheduled = []
    done = []

with open("config.yaml", 'r') as stream:
    try:
        downloads.config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("invalid config")
        raise exc

# Because stream is not a copy, but a pointer, there is no need to
# implement rescheduling logic, simply syncing should do the trick
def schedule_download(stream, output, final_folder, final_name):
    downloads.scheduled.append(stream.url)
    started = False
    while not stream.url in downloads.done:
        time.sleep(10)
        current_time = datetime.datetime.utcnow()
        stream_time = stream.starttime
        if stream_time > current_time:
            continue
        if not started:
            print("Starting to archive {}".format(stream.title_jp))
            started = True

        class MyLogger(object):
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                if "This live event will begin in" in msg:
                    return

                if "This video is available to this channel's members" in msg:
                    print("{} is a members only stream, can't archive it".format(stream.title_jp))
                    downloads.done.append(stream.url)
                    return

        ydl_opts = {
            'outtmpl': output,
            'merge_output_format': 'mkv',
            'ignoreerrors': True,
            'quiet': True,
            'logger': MyLogger(),
        }

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        download = ydl.download([stream.url])
        if int(download) != 0:
            continue # Retry untill it works

        return asyncio.run(finish_download(stream, output, final_folder, final_name))

    pass

async def finish_download(stream, output, final_folder, final_name):
    # Handle streams once they're finished
    shutil.move(output, f"{final_folder}/{final_name}")
    downloads.done.append(stream.url)
    print("Succesfully archived {}".format(stream.title_jp))
    pass

async def update_scheduled_streams():
    streams = await hololive.get_streams()
    print(streams)
    for stream in streams:
        if stream.url in downloads.scheduled or stream.url in downloads.done:
            continue

        category = ""
        for cat in downloads.config["categories"]:
            for word in downloads.config["categories"][cat]:
                if re.search(word, stream.title_jp, re.IGNORECASE):
                    category = cat
        if category == "":
            continue
        
        output = "{}/{}.mkv".format(downloads.config["locations"]["tmp"], stream.url.split("?v=")[1])
        final_folder = f"{downloads.config['locations']['final']}/{category}/{stream.title_jp.replace('/','')}"
        final_name = f"{stream.title_jp.replace('/','')}.mkv"
        final_output = f"{final_folder}/{final_name}"

        if pathlib.Path(final_output).exists():
            # Stream is already downloaded
            downloads.done.append(stream.url)
            continue
        
        os.makedirs(downloads.config["locations"]["tmp"], exist_ok=True)
        os.makedirs(final_folder, exist_ok=True)

        print("{} is a wanted {} stream. Planning to archive it!".format(stream.title_jp, category))
        t = threading.Thread(target=schedule_download,args=(stream,output,final_folder,final_name))
        t.start()

async def periodic_updates():
    while True:
        await update_scheduled_streams()
        await asyncio.sleep(300)

try:
    asyncio.run(periodic_updates())
except KeyboardInterrupt:
    sys.exit(0)