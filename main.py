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

class downloads:
    config = {}
    scheduled = {}
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
    if pathlib.Path(final_output).exists():
        downloads.done.append(stream["youtube_url"])
        return
    while not stream["youtube_url"] in downloads.done:
        time.sleep(10)
        current_time = datetime.datetime.utcnow()
        stream_time = stream["datetime"]
        if stream_time > current_time:
            continue
        cmd = ["youtube-dl", stream["youtube_url"], "--merge-output-format", "mkv", "-o", output]
        print(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate()
        if p.returncode != 0 or not pathlib.Path(output).exists():
            print(stream)
            continue # Retry untill it works

        return finish_download(stream, output, final_output)

    pass

def finish_download(stream, output, final_output):
    # Handle streams once they're finished
    shutil.move(output, final_output)
    downloads.done.append(stream["youtube_url"])
    pass

for day in hololive.streams.schedule["schedule"]:
    for stream in day["schedules"]:
        category = ""
        for cat in downloads.config["categories"]:
            for word in downloads.config["categories"][cat]:
                if re.search(word, stream["title"], re.IGNORECASE):
                    category = cat
        if category == "":
            continue
        print("{} is a wanted {} stream. Planning to archive it!".format(stream["title"],category))

        output = "{}/{}.mkv".format(downloads.config["locations"]["tmp"], stream["youtube_url"].split("?v=")[1])
        final_output = "{}/{}/{}.mkv".format(
            downloads.config["locations"]["final"],
            category,
            stream["title"].replace("/","") # To make sure it doesn't try to create a subdirectory
        )
        t = threading.Thread(target=schedule_download,args=(stream,output,final_output))
        t.start()

try:
    input()
except:
    sys.exit(0)