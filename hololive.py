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

sync()
streams.sync_thread = threading.Thread(target=periodic_sync, daemon=True)
streams.sync_thread.start()

if __name__ == "__main__":
    
    pass