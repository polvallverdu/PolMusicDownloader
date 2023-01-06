import tidalapi
import pickle
import os
import uuid
import time
import random
from modules.utils.download_utils import get_download_path
import modules.processors.normalizer as normalizer

SESSION_PATH = "./secrets/session.p"

def random_delay():
  # Random delay between 0.5 and 5 seconds
  delay = random.randint(500, 5000) / 1000
  print("Sleeping for " + str(delay) + " seconds")
  time.sleep(delay)
  print("Done sleeping")

class TidalClient:
  
  def __init__(self):
    self.session: tidalapi.Session = None if not os.path.exists(SESSION_PATH) else pickle.load(open(SESSION_PATH, "rb"))
    self.login()
  
  def login(self):
    if self.session is None or not self.session.check_login():
      print("Invalid session, logging in again")
      self.session = tidalapi.Session()
      
      # TODO: Login with playwright + load dotenv
      # success = session.login(os.getenv('TIDAL_USERNAME'), os.getenv('TIDAL_PASSWORD'))
      
      success = self.session.login_oauth_simple()
      
      if success:
        pickle.dump(self.session, open(SESSION_PATH, "wb"))
      else: 
        print("Failed to login to Tidal")
        exit(1)
    print("Logged in to Tidal")
  
  def query(self, query: str, type: list=[]):
    # tidalapi.session.SearchTypes
    # SearchTypes = [tidalapi.Artist,
    #            tidalapi.Album,
    #            tidalapi.Track,
    #            tidalapi.Video,
    #            tidalapi.Playlist,
    #            None]
    
    # result = {
    #         'artists': self.request.map_json(json_obj['artists'], self.parse_artist),
    #         'albums': self.request.map_json(json_obj['albums'], self.parse_album),
    #         'tracks': self.request.map_json(json_obj['tracks'], self.parse_track),
    #         'videos': self.request.map_json(json_obj['videos'], self.parse_video),
    #         'playlists': self.request.map_json(json_obj['playlists'], self.parse_playlist)
    #     }
    
    return self.session.search(query, type)
  
  def track(self, track_id: int) -> tidalapi.Track:
    return self.session.track(track_id)
  
  def album(self, album_id: int) -> tidalapi.Album:
    return self.session.album(album_id)
  
  def artist(self, artist_id: int) -> tidalapi.Artist:
    return self.session.artist(artist_id)
  
  def playlist(self, playlist_id: int) -> tidalapi.Playlist:
    return self.session.playlist(playlist_id)
  
  def format_data(self, track: tidalapi.Track) -> dict:
    album: tidalapi.Album = track.album
    artists: list[tidalapi.Artist] = track.artists
    
    lyrics: tidalapi.media.Lyrics
    try:
      lyrics = track.lyrics()
    except:
      lyrics = None
    
    data = {
      "platform": "tidal",
      "id": track.id,
      "title": track.name,
      "explicit": track.explicit,
      "thumbnail": album.image(1280),
      #"thumbnail_video": album.video(1280),
      "url": f"https://tidal.com/browse/track/{track.id}",
      "album": album.name,
      "tags": [],
      "description": track.copyright,
      "duration": track.duration,
      "upload_date": track.tidal_release_date.timestamp(),
      "uploader": [artist.name for artist in artists],
      "uploader_id": album.artist.id,
      "popularity": {
        "tidal": track.popularity,
      },
      "track_number": track.track_num,
      "volume_number": track.volume_num,
    }
    
    if album.video_cover:
      data["thumbnail_video"] = album.video(1280)
    
    if lyrics:
      data["lyrics"] = lyrics.subtitles
    
    return data

  # Normalizing
  # def download_track(self, track: tidalapi.Track) -> tuple[uuid.UUID, str, dict]:
  #   download_uuid = uuid.uuid4()
  #   formatted_data = self.format_data(track)
  #   formatted_data["uuid"] = str(download_uuid)
    
  #   path = get_download_path(formatted_data)
  #   download_path = f"{path}/song.flac"
  #   download_pathnn = download_path.replace(".flac", "_nn.flac")
    
  #   download_url = track.get_url()
  #   os.system('ffmpeg -i "{}" -af aresample=resampler=soxr -ar 44100 "{}"'.format(download_url, download_pathnn))
  #   random_delay()
  #   if not os.path.exists(download_pathnn):
  #     return None, None, None
    
  #   normalizer.process_path(download_pathnn, download_path)
  #   os.remove(download_pathnn)
    
  #   return download_uuid, path, formatted_data
  
  def download_track(self, track: tidalapi.Track) -> tuple[uuid.UUID, str, dict]:
    download_uuid = uuid.uuid4()
    formatted_data = self.format_data(track)
    formatted_data["uuid"] = str(download_uuid)
    
    path = get_download_path(formatted_data)
    download_path = f"{path}/song.flac"
    
    download_url = track.get_url()
    os.system('ffmpeg -i "{}" -af aresample=resampler=soxr -ar 44100 "{}"'.format(download_url, download_path))
    random_delay()
    if not os.path.exists(download_path):
      return None, None, None
    
    formatted_data["peak"] = normalizer.get_peak_path(download_path)
    
    return download_uuid, path, formatted_data

STATICTIDAL = TidalClient()