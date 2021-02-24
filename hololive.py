import requests
import json
import threading
import time
import urllib.request
import json
import urllib

class streams:
    schedule = {}
    sync_thread = None

def sync():
    res = requests.request("GET", "http://127.0.0.1:5000/schedules")
    schedule = json.loads(res.text)
    for date in schedule['schedule']:
        for stream in date['schedules']:
            stream["title"] = get_youtube_title(stream["youtube_url"])

def periodic_sync():
    while True:
        """Sync every 1 minute, no rate limiting is needed,
        but it makes it so that python isn't busy with a sync all the time"""
        time.sleep(60)
        sync()

# From https://stackoverflow.com/questions/59627108/retrieve-youtube-video-title-using-api-python
def get_youtube_title(youtube_url):
    params = {"format": "json", "url": youtube_url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return data['title']

sync()
streams.sync_thread = threading.Thread(target=periodic_sync, daemon=True)
streams.sync_thread.start()

if __name__ == "__main__":
    
    pass