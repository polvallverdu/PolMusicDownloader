import pika
import json
import os
import logging

DOWNLOAD_QUEUE = "music_songdownloader"
FINISHED_DOWNLOAD_QUEUE = "music_finishedsongdownloader"
STEM_QUEUE = "music_songspleeter"
FINISHED_STEM_QUEUE = "music_finishedsongspleeter"


class RabbitMQ:
  
  def __init__(self):
    self.connection = pika.BlockingConnection(pika.URLParameters(os.getenv("RABBITMQ_URI")))
    self.channel = self.connection.channel()
    print("Connected to RabbitMQ")
    self.deliverytags = []
  
  def declare_queue(self, name: str):
    print(f"Declaring queue {name}")
    self.channel.queue_declare(queue=name, durable=True)
  
  def send_ack(self, deliverytag, valid: bool):
    print(f"Sending ack {valid} to {deliverytag}")
    if valid:
      self.channel.basic_ack(delivery_tag=deliverytag)
    else:
      self.channel.basic_nack(delivery_tag=deliverytag)
  
  def register_callback(self, queue: str, callback, auto_ack: bool = True):
    print(f"Registering callback for {queue}")
    def new_callback(ch, method, properties, body):
      self.deliverytags.append(method.delivery_tag)
      self.send_ack(method.delivery_tag, callback(ch, method, properties, body))
      self.deliverytags.remove(method.delivery_tag)
    
    self.channel.basic_consume(queue=queue, on_message_callback=new_callback, auto_ack=auto_ack)
  
  def publish_song_download(self, url: str):
    print(f"Publishing song download {url}")
    d = {
      "url": url,
    }
    self.channel.basic_publish("", routing_key=DOWNLOAD_QUEUE, body=json.dumps(d), properties=pika.BasicProperties(delivery_mode=2))
  
  def publish_finish_download(self, uuid: str, data: dict):
    print(f"Publishing finish download {uuid}")
    d = {
      "uuid": uuid,
      "data": data.copy(),
    }
    self.channel.basic_publish("", routing_key=FINISHED_DOWNLOAD_QUEUE, body=json.dumps(d), properties=pika.BasicProperties(delivery_mode=2))
  
  def publich_finish_stem(self, uuid: str, version: str):
    print(f"Publishing finish stem {uuid}")
    d = {
      "uuid": uuid,
      "version": version,
    }
    self.channel.basic_publish("", routing_key=FINISHED_STEM_QUEUE, body=json.dumps(d), properties=pika.BasicProperties(delivery_mode=2))
  
  def start(self):
    print("Starting RabbitMQ")
    self.channel.start_consuming()
  
  def stop(self):
    for tag in self.deliverytags:
      self.send_ack(tag, False)
    self.channel.close()
    self.connection.close()


STATICRABBITMQ = RabbitMQ()
