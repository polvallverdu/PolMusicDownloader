import os

def get_download_path(formatted_data: dict) -> str:
  # Should go to os.getenv("VOLUME")/downloads/uuid/song.flac
  song_uuid = formatted_data['uuid']
  return f'{os.getenv("VOLUME")}/downloads/song_uuid/{song_uuid}.flac'