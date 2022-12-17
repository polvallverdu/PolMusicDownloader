from dotenv import load_dotenv
load_dotenv()

import os

import modules.downloaders.tidal as t 
import modules.database as db

tidal = t.TidalClient()
database = db.DatabaseClient()


