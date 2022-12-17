import os
from subprocess import Popen, DEVNULL, STDOUT, PIPE
import soundfile as sf
# import dotenv
# dotenv.load_dotenv()

def get_path():
  if os.name == "nt":  # Windows
    return "./opus/opusenc.exe"
  #elif os.name == "posix":  # Linux
  else:
    return "opusenc"


# input_file = sf.SoundFile(input_file_path, 'r')
# songbytes = input_file.read().tobytes()
#p = Popen([path, '--discard-comments', '--discard-pictures', '--music', '--bitrate 128', '--raw', '--raw-rate 44100', '--raw-chan 2'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
#p = Popen([path, '--raw', '--raw-rate 44100', '--raw-chan 2', '-', '-'], stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, bufsize=len(songbytes))

# print(len(songbytes))
# p.stdin.write(songbytes)
# p.stdin.flush()
# p.stdin.close()
# #p.stdin.write(input_file_path.encode('utf-8'))
# # output_file = sf.SoundFile(output_file_path, 'x', 48000, 2, 'OPUS', format='OGG')
# # output_file.buffer_write(p.stdout.read(), "float32")
# print(p.stdout.read())
# output_file = open(output_file_path, 'wb')
# output_file.write(p.stdout.read())
# output_file.close()

def encode_opus(song_uuid: str):
  input_file_path = f'{os.getenv("VOLUME")}/files/{song_uuid}/song.flac'
  versions_dir_path = f'{os.getenv("VOLUME")}/files/{song_uuid}/versions'
  output_file_path = f'{os.getenv("VOLUME")}/files/{song_uuid}/versions/compressed_128_nometadata.opus'
  
  if os.path.exists(output_file_path):
    return
  
  if not os.path.exists(versions_dir_path):
    os.mkdir(versions_dir_path)

  Popen([get_path(), '--discard-comments', '--discard-pictures', '--bitrate', '128', '--music', '--quiet', input_file_path, output_file_path])
  