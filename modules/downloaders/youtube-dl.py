import youtube_dl
import uuid
import os
import soundfile as sf
import numpy as np
import math
import shutil
import modules.processors.normalizer as normalizer
from modules.utils.download_utils import get_download_path

YDL_OPTS = {
  'format': 'bestaudio/best',
  'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'flac',
  }],
  'outtmpl': '%(title)s.%(etx)s',
  'quiet': True,
  'noplaylist': True,
  'no_color': True,
  'writethumbnail': False,
  'allsubtitles': False,
}

def search_youtube(query: str) -> dict:
  with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    return ydl.extract_info(f"ytsearch:{query}", download=False)

def search_soundcloud(query: str) -> dict:
  with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    return ydl.extract_info(f"scsearch:{query}", download=False)

def get_platform(info_dict: dict) -> str:
  if "soundcloud.com" in info_dict["uploader_url"]:
    return "soundcloud"
  elif "youtube.com" in info_dict["uploader_url"]:
    return "youtube"
  return "unknown"

def format_data(info_dict: dict) -> dict:
  return {
    "platform": info_dict["extractor"].lower(),
    "id": info_dict["id"],
    "title": info_dict["track"] if "track" in info_dict else info_dict["title"],
    "thumbnail": info_dict["thumbnail"],
    "url": info_dict["url"],
    "album": info_dict["album"] if "album" in info_dict else info_dict["title"],
    "tags": info_dict["tags"] if "tags" in info_dict else [],
    "description": info_dict["description"] if "description" in info_dict else "",
    "duration": info_dict["duration"],
    "upload_date": info_dict["upload_date"],
    "uploader": (info_dict["creator"] if "creator" in info_dict else info_dict["uploader"]).split(", "),
    "uploader_id": info_dict["uploader_id"],
    "popularity": {
      "view_count": info_dict["view_count"] if "view_count" in info_dict else 0,
      "like_count": info_dict["like_count"] if "like_count" in info_dict else 0,
      "comment_count": info_dict["comment_count"] if "comment_count" in info_dict else 0,
      "repost_count": info_dict["repost_count"] if "repost_count" in info_dict else 0,
    }
  }

def download_song(url: str) -> tuple(uuid.UUID, str, dict)|None:
  with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    info_dict = ydl.extract_info(url, download=False)
    formatted_data = format_data(info_dict)
    download_uuid = uuid.uuid4()
    formatted_data["uuid"] = str(download_uuid)
    
    download_path = get_download_path(formatted_data)
    download_pathnn = download_path.replace(".flac", "_nn.flac")
    
    # Download the song with ffmpeg
    os.system('ffmpeg -i "{}" -af aresample=resampler=soxr -ar 44100 "{}"'.format(info_dict["url"], download_pathnn))
    if not os.path.exists(download_pathnn):
      return None
    
    normalizer.process_path(download_pathnn, download_path)
    os.remove(download_pathnn)
    
    return download_uuid, download_path, formatted_data
