import numpy as np
import soundfile as sf
import os
import shutil
import uuid
import math

# from dotenv import load_dotenv
# load_dotenv()

MODEL = "htdemucs_ft"
STEMS = ["bass.wav", "other.wav", "drums.wav", "vocals.wav"]
FINAL_STEMS = ["instrument.flac", "drums.flac", "vocals.flac"]
CHUNK_SIZE = 44100*4


def get_song_folder(song_uuid: str) -> str|None:
  song_folder = f'{os.getenv("VOLUME")}/files/{song_uuid}'
  if not os.path.exists(song_folder):
    return None
  return song_folder


def get_song_stems_folder(separation_id: str, song_folder: str) -> tuple[str, str, str]:
  if not os.path.exists(f'{song_folder}/stems'):
    os.mkdir(f'{song_folder}/stems')
  stem_folder = f'{os.getenv("VOLUME")}/separation/{separation_id}'
  return stem_folder, f'{stem_folder}/{MODEL}', f'{song_folder}/stems/{separation_id}'


def check_stems(stems: list[str]) -> bool:
  for stem in stems:
    if not os.path.exists(stem):
      return False
  return True


def separate_song(song_uuid: str) -> bool:
  separation_id = str(uuid.uuid4())
  song_folder = get_song_folder(song_uuid)
  if not song_folder:
    return False

  stem_folder, proccesed_stems_folder, final_stem_folder = get_song_stems_folder(separation_id, song_folder)
  stems = []
  for stem in STEMS:
    stems.append(f'{proccesed_stems_folder}/{stem}')
  
  ########    SPLITTING SONG     ########
  os.system("demucs {} -n {} -o {} --filename {}".format(f'{song_folder}/song.flac', MODEL, stem_folder, "{stem}.{ext}"))

  if not check_stems(stems):
    return False

  os.mkdir(final_stem_folder)

  ########    CREATING INSTRUMENTS FILE     ########
  bass_file = sf.SoundFile(stems[0], 'r')
  bass_file._prepare_read(0, None, bass_file.frames)
  other_file = sf.SoundFile(stems[1], 'r')
  other_file._prepare_read(0, None, other_file.frames)

  instrument_file = sf.SoundFile(f'{final_stem_folder}/{FINAL_STEMS[0]}', 'x', 44100, 2, 'PCM_16', format='FLAC')
  for i in range(math.ceil(bass_file.frames / CHUNK_SIZE)):
    bass_chunk = bass_file.read(CHUNK_SIZE, dtype="float32")
    other_chunk = other_file.read(CHUNK_SIZE, dtype="float32")
    instrument_file.write((bass_chunk + other_chunk) / 2)
    
    del bass_chunk, other_chunk

  bass_file.close()
  other_file.close()
  instrument_file.close()

  ########    SAVING OTHER STEMS     ########
  drums_pcm, _ = sf.read(stems[2], dtype="float32")
  vocals_pcm, _ = sf.read(stems[3], dtype="float32")
  sf.write(f'{final_stem_folder}/{FINAL_STEMS[1]}', drums_pcm, 44100, format='flac', subtype="PCM_16")
  sf.write(f'{final_stem_folder}/{FINAL_STEMS[2]}', vocals_pcm, 44100, format='flac', subtype="PCM_16")

  del drums_pcm, vocals_pcm

  shutil.rmtree(stem_folder)
  return True
