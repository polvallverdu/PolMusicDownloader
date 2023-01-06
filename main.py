from dotenv import load_dotenv
load_dotenv()
import time
import signal
import json

from modules.databases.rabbitmq import STATICRABBITMQ as rabbitmq
from modules.databases.rabbitmq import DOWNLOAD_QUEUE, FINISHED_DOWNLOAD_QUEUE, FINISHED_STEM_QUEUE, STEM_QUEUE
queues = [DOWNLOAD_QUEUE, FINISHED_DOWNLOAD_QUEUE, FINISHED_STEM_QUEUE, STEM_QUEUE]
from modules import workers


def register_callbacks():
  def download_callback(ch, method, properties, body):
    data = json.loads(body)
    return workers.download_worker(data["url"])

  def split_callback(ch, method, properties, body):
    data = json.loads(body)
    return workers.split_worker(data["uuid"])
  
  rabbitmq.register_callback(DOWNLOAD_QUEUE, download_callback, False)
  rabbitmq.register_callback(STEM_QUEUE, split_callback, False)
  


def main() -> None:
  def sigterm(_, __):
    print("SIGTERM received, shutting down")
    rabbitmq.stop()
    exit(0)
  signal.signal(signal.SIGINT, sigterm)
  for queue in queues:
    rabbitmq.declare_queue(queue)
  register_callbacks()
  rabbitmq.start()
  
  # while True:
  #   time.sleep(1)

if __name__ == "__main__":
  # TODO: Use logging
  main()
