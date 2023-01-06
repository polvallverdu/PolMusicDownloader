import os

def get_download_path(formatted_data: dict) -> str:
  # Should go to os.getenv("VOLUME")/downloads/uuid/song.flac
  song_uuid = formatted_data['uuid']
  path = f'{os.getenv("VOLUME")}/downloads/{song_uuid}'
  os.makedirs(path, exist_ok=True)
  return path
