import pymongo
import os

class DatabaseClient:
  
  def __init__(self):
    self.client = pymongo.MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)