import requests
import json
import threading
import time

class streams:
    schedule = {}
    sync_thread = None

def sync():
    res = requests.request("GET", "http://127.0.0.1:5000/schedules")
    streams.schedule = json.loads(res.text)

def periodic_sync():
    while True:
        """Sync every 1 minute, no rate limiting is needed,
        but it makes it so that python isn't busy with a sync all the time"""
        time.sleep(60)
        sync()
        
sync()
streams.sync_thread = threading.Thread(target=periodic_sync, daemon=True)
streams.sync_thread.start()

if __name__ == "__main__":
    
    pass