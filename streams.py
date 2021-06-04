from typing import List
from datetime import datetime
from threading import Thread
from asyncio import sleep
from os import makedirs
from config import locations, add_stream, streams
from pathlib import Path
from youtube_dl import YoutubeDL
from shutil import move
from documentation import generate_documentation
from asyncio import run

class Stream(object):
  def __new__(cls, title: str, youtube_id: str, start_datetime: datetime, automatic: bool, download: bool, output_override: str=""):
    for existing_stream in streams:
      if existing_stream.youtube_id == youtube_id:
        existing_stream.title = title
        existing_stream.start_datetime = start_datetime
        existing_stream.automatic = automatic
        existing_stream.download = download
        existing_stream.run()
        raise Exception("Stream already exists")
    return super(Stream, cls).__new__(cls)
  def __init__(self, title: str, youtube_id: str, start_datetime: datetime, automatic: bool, download: bool, output_override: str=""):
    
    self.title = title
    self.safe_title = self.title.replace('/','').replace('\\','')
    self.youtube_id = youtube_id
    self.start_datetime = start_datetime
    self.youtube_url = f"https://youtube.com/watch?v={youtube_id}"
    self.final_folder = f"{(locations['final'] or output_override)}/{self.safe_title}"
    self.final_output = f"{self.final_folder}/{self.safe_title}.mkv"
    self.tmp_output = f"{locations['tmp']}/{self.youtube_id}.mkv"
    makedirs(locations["tmp"], exist_ok=True)
    makedirs(self.final_folder, exist_ok=True)
    self.ignore = "DOWNLOADED" if Path(self.final_output) else (False if download else ("CATEGORY" if automatic else "USER"))
    self.run()

  def run(self):
    if getattr(self, "thread", False): return
    self.thread = Thread(target=run, args=(self._scheduler(),))
    self.thread.daemon = True
    self.thread.start()
  async def _attempt_download(self):
    print(f"[DOWNLOADER] Attempting to download {self.title} to {self.final_output}")
    class ytdl_logger(object):
      def __init__(self, target: Stream): self.target = target
      def debug(self, msg): pass
      def warning(self, msg): pass
      def error(self, msg):
        if "This live event will begin in" in msg:
          return
        if "This video is available to this channel's members" in msg:
          self.target.ignore = "MEMBERS_ONLY"
          return
    ydl_opts = {
      'outtmpl': self.tmp_output,
      'merge_output_format': 'mkv',
      'ignoreerrors': True,
      'quiet': True,
      'logger': ytdl_logger(self),
    }
    ydl = YoutubeDL(ydl_opts)
    download = ydl.download([self.youtube_url])
    if int(download) != 0: return
    await self._finish_download()

  async def _scheduler(self):
    while not self.ignore:
      await sleep(10)
      if self.start_datetime > datetime.utcnow(): continue
      await self._attempt_download()

  async def _finish_download(self):
    move(self.tmp_output, self.final_output)
    with open(f"{self.final_folder}/about.md", 'w') as docfile:
      docfile.write(generate_documentation(self.final_output))
    print(f"[DOWNLOADER] Succesfully archived {self.title}")
    self.ignore = "DOWNLOADED"

if __name__ == '__main__':
  streams = []
  streams.append(Stream("Gawr Gura sings Kimi No Toriko (Summertime)", "ng_Vrp7vFAw", datetime.now(), False, True))
  streams.append(Stream("Polka you can't say the gamer word!!!", "DqYPptPST3o", datetime.now(), False, False))
  for Stream in streams:
    Stream.thread.join()