from typing import List
from datetime import datetime
from threading import Thread
from asyncio import sleep
from os import makedirs
from config import locations, add_stream, streams
from pathlib import Path
from subprocess import Popen, DEVNULL, PIPE
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
    self.final_folder = f"{(output_override or locations['final'])}/{self.safe_title}"
    self.final_output = f"{self.final_folder}/{self.safe_title}"
    self.tmp_output = f"{locations['tmp']}/{self.youtube_id}"
    self.ignore = "DOWNLOADED" if Path(self.final_output).exists() else (False if download else ("CATEGORY" if automatic else "USER"))
    self.run()

  def run(self):
    if getattr(self, "thread", False): return
    self.thread = Thread(target=run, args=(self._scheduler(),))
    self.thread.daemon = True
    self.thread.start()
  async def _attempt_download(self):
    print(f"[DOWNLOADER] Attempting to download {self.title} to {self.final_output}")
    download_process = Popen([
      "yt-dlp",
      "--write-info-json",
      "--keep-video",
      "--remux-video", "mkv",
      "--write-thumbnail",
      "--sub-langs", "all",
      "--sub-format", "srv3/json",
      "--write-subs",
      "-o", self.tmp_output + ".%(ext)s",
      self.youtube_url], stdout=DEVNULL, stderr=PIPE)
    download_process.wait()
    stderr=download_process.stderr.read().decode('utf-8')
    if "This live event will begin in" in stderr:
      return
    elif "This video is available to this channel's members" in stderr:
      self.ignore = "MEMBERS_ONLY"
      return
    if int(download_process.returncode) != 0: return
    await self._finish_download()

  async def _scheduler(self):
    while not self.ignore:
      await sleep(10)
      if self.start_datetime.replace(tzinfo=None) > datetime.utcnow().replace(tzinfo=None): continue
      await self._attempt_download()

  async def _finish_download(self):
    makedirs(self.final_folder, exist_ok=True)
    move(self.tmp_output + ".mkv", self.final_output + ".mkv")
    move(self.tmp_output + ".info.json", self.final_output + ".info.json")
    move(self.tmp_output + ".live_chat.json", self.final_output + ".live_chat.json")
    move(self.tmp_output + ".webp", self.final_folder + "/cover.webp")
    with open(f"{self.final_folder}/about.md", 'w') as docfile:
      docfile.write(generate_documentation(self.final_output + '.mkv'))
    print(f"[DOWNLOADER] Succesfully archived {self.title}")
    self.ignore = "DOWNLOADED"

if __name__ == '__main__':
  streams = []
  streams.append(Stream("Gawr Gura sings Kimi No Toriko (Summertime)", "ng_Vrp7vFAw", datetime.now(), False, True))
  streams.append(Stream("Polka you can't say the gamer word!!!", "DqYPptPST3o", datetime.now(), False, False))
  for Stream in streams:
    Stream.thread.join()