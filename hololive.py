import requests
import json
import threading
import time
import urllib.request
import json
import urllib
import datetime
import pytz
import os

class streams:
    schedule = {}
    sync_thread = None

api_url = os.getenv('API_URL', 'https://hololive-api.marnixah.com/schedules')

def sync():
    res = requests.request("GET", api_url)
    schedule = json.loads(res.text)
    for date in schedule['schedule']:
        for stream in date['schedules']:
            day_arr = date["date"].split("/")
            month = int(day_arr[0])
            day = int(day_arr[1])

            time_arr = stream["time"].split(":")
            hour = int(time_arr[0])
            minute = int(time_arr[1])

            current_time = datetime.datetime.utcnow()
            year = current_time.year
            if current_time.month == 1:
                current_time.year += 1 # So stuff can be scheduled at the end of the year

            stream["datetime"] = datetime.datetime(
                year, month, day, hour, minute
            ) - datetime.timedelta(hours=9) # JST is 9 hours ahead of UTC

            stream["title"] = get_youtube_title(stream["youtube_url"])
    streams.schedule = schedule

def periodic_sync():
    while True:
        # Sync every 30 minutes, this is so we don't trigger a youtube ratelimit
        time.sleep(30 * 60)
        synced = False
        while not synced:
            try:
                sync()
                synced = True
            except:
                pass

# From https://stackoverflow.com/questions/59627108/retrieve-youtube-video-title-using-api-python
def get_youtube_title(youtube_url):
    params = {"format": "json", "url": youtube_url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    with urllib.request.urlopen(req) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return data['title']

sync()
streams.sync_thread = threading.Thread(target=periodic_sync, daemon=True)
streams.sync_thread.start()

if __name__ == "__main__":
    
    pass