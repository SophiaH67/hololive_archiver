import time
import hololive
import threading
import datetime
import subprocess
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
def schedule_download(stream, output, final_output):
    downloads.scheduled.append(stream["youtube_url"])

    while not stream["youtube_url"] in downloads.done:
        time.sleep(10)
        current_time = datetime.datetime.utcnow()
        stream_time = stream["datetime"]
        if stream_time > current_time:
            continue
        print("Starting to archive {}".format(stream["title"]))

        class MyLogger(object):
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                if "This live event will begin in" in msg:
                    return

                if "This video is available to this channel's members" in msg:
                    print("{} is a members only stream, can't archive it".format(stream["title"]))
                    downloads.done.append(stream["youtube_url"])
                    return

        ydl_opts = {
            'outtmpl': output,
            'merge_output_format': 'mkv',
            'ignoreerrors': True,
            'quiet': True,
            'logger': MyLogger(),
        }

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        download = ydl.download([stream["youtube_url"]])
        if int(download) != 0:
            continue # Retry untill it works

        return finish_download(stream, output, final_output)

    pass

def finish_download(stream, output, final_output):
    # Handle streams once they're finished
    shutil.move(output, final_output)
    downloads.done.append(stream["youtube_url"])
    print("Succesfully archived {}".format(stream["title"]))
    pass

def update_scheduled_streams():
    for day in hololive.streams.schedule["schedule"]:
        for stream in day["schedules"]:
            if stream["youtube_url"] in downloads.scheduled or stream["youtube_url"] in downloads.done:
                continue

            category = ""
            for cat in downloads.config["categories"]:
                for word in downloads.config["categories"][cat]:
                    if re.search(word, stream["title"], re.IGNORECASE):
                        category = cat
            if category == "":
                continue
            
            output = "{}/{}.mkv".format(downloads.config["locations"]["tmp"], stream["youtube_url"].split("?v=")[1])
            final_output = "{}/{}/{}.mkv".format(
                downloads.config["locations"]["final"],
                category,
                stream["title"].replace("/","") # To make sure it doesn't try to create a subdirectory
            )

            if pathlib.Path(final_output).exists():
                # Stream is already downloaded
                downloads.done.append(stream["youtube_url"])
                continue
            
            os.makedirs(downloads.config["locations"]["tmp"], exist_ok=True)
            os.makedirs(pathlib.Path(final_output).parents[0], exist_ok=True)

            print("{} is a wanted {} stream. Planning to archive it!".format(stream["title"],category))
            t = threading.Thread(target=schedule_download,args=(stream,output,final_output))
            t.start()

def periodic_updates():
    while True:
        update_scheduled_streams()
        time.sleep(300)

try:
    periodic_updates()
except KeyboardInterrupt:
    sys.exit(0)