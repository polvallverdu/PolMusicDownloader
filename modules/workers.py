import modules.downloaders.youtubedl as ydl
import modules.downloaders.tidal as tidal
import modules.processors.song_splitter as splitter
import modules.databases.rabbitmq as rabbitmq
import os
import shutil
import requests
import logging

def exists_song(fields: dict) -> bool:
  return False

def exists_album(fields: dict) -> bool:
  return False

def get_all_tracks_from_tidal(obj) -> list[tidal.tidalapi.Track]:
  tracks: list[tidal.tidalapi.Track] = obj.tracks()
  num_tracks = obj.num_tracks
  
  if len(tracks) == num_tracks:
    return tracks

  while len(tracks) < num_tracks:
    tracks.extend(obj.tracks(offset=len(tracks)))
  
  return tracks


def download_worker(url: str) -> bool:
  print(f"Download worker started for {url}")
  # data = ydl.get_song_data(url)
  # res = Song.prisma().find_first(where={
  #   "originalPlatform": data["platform"],
  #   "originalId": data["id"]
  # })
  # if res:
  #   print("Song already exists")
  #   return True # Song already exists
  # TODO: Check if song already exists
  
  if "tidal.com/browse" in url:
    # This is a tidal url https://tidal.com/browse/album/258383177/
    if url.endswith("/"):
      url = url[:-1]
    tidal_id = url.split("/")[-1]
    print(f"[{url}] Tidal id: {tidal_id}")
    
    tracks = []
    obj = None
    
    if "album" in url:
      obj = tidal.STATICTIDAL.album(int(tidal_id))
    elif "playlist" in url:
      obj = tidal.STATICTIDAL.playlist(int(tidal_id))
    elif "track" in url:
      obj = tidal.STATICTIDAL.track(int(tidal_id))

    # if obj is not an object with class tidal.tidalapi.Track, print hello
    if not isinstance(obj, tidal.tidalapi.Track):
      print(f"[{url}] Not a tidal track")
      tracks = get_all_tracks_from_tidal(obj)
      for track in tracks:
        # TODO: CHECK IF TRACK ALREADY EXISTS
        rabbitmq.STATICRABBITMQ.publish_song_download(f"https://tidal.com/browse/track/{track.id}")
      
      return True

    print(f"[{url}] Downloading from tidal...")
    songuuid, path, data = tidal.STATICTIDAL.download_track(obj)
  else:
    print(f"[{url}] Downloading from ydl...")
    songuuid, path, data = ydl.download_song(url)
  if not songuuid:
    return False
  
  # TODO: Check if downloading the cover is needed
  # Download cover
  print(f"[{url}] Downloading covers...")
  if "thumbnail_video" in data:
    coverurl = data["thumbnail_video"]
    print(f"[{url}] Downloading video cover -> {coverurl}")
    r = requests.get(coverurl)
    with open(f"{path}/cover.mp4", "wb") as f:
      f.write(r.content)
    print(f"[{url}] Saved video cover")
  if "thumbnail" in data:
    coverurl = data["thumbnail"]
    print(f"[{url}] Downloading cover -> {coverurl}")
    r = requests.get(coverurl)
    with open(f"{path}/cover.jpg", "wb") as f:
      f.write(r.content)
    print(f"[{url}] Saved cover")
  
  rabbitmq.STATICRABBITMQ.publish_finish_download(str(songuuid), data)
  
  return True
  # song_path = f'{os.getenv("VOLUME")}/{songuuid}/'
  # os.mkdir(song_path)
  # shutil.move(path, song_path)
  # # TODO: Add thumnails
  
  # # Creating compressed version of song
  # compressed_filename = opus.encode_opus(songuuid)
  # SongData.prisma().create(data={
  #   "id": songuuid,
  #   "compressed": True,
  #   "compressedFile": compressed_filename,
  #   "ogFile": "song.flac",
  #   "stems": False,
  # })
  

def split_worker(songuuid) -> bool:
  print(f"Received new split request {songuuid}")
  separation_id = splitter.separate_song(str(songuuid))
  
  if not separation_id:
    print(f"Couldn't split {songuuid}")
    return False

  version = "demucs1"

  print(f"Finished splitting {songuuid} on version {version}")
  rabbitmq.STATICRABBITMQ.publich_finish_stem(str(songuuid), version)
  return True