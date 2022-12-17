import os
import soundfile as sf
import numpy as np

def process_path(in_file_path: str, out_file_path: str):
  file = sf.SoundFile(in_file_path)
  file_out = sf.SoundFile(out_file_path, mode='x', samplerate=44100, channels=2, subtype='PCM_16', format="FLAC")
  readed_file = file.read(dtype='float32')
  
  peak = get_peak(readed_file)
  out = process(readed_file, peak)
  
  file_out.write(out)
  del out, readed_file
  file.close()
  file_out.close()
  
  return peak

def get_peak(in_np: np.ndarray) -> float:
  return np.abs(in_np).max()

def process(in_np: np.ndarray, peak=None) -> np.ndarray:
  peak = get_peak(in_np) if peak is None else peak
  dif = 1 / peak
  f_file = in_np * dif
  return f_file
