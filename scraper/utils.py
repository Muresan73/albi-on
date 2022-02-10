from enum import Enum
import os
from typing import List, Tuple
from pymongo import MongoClient


USER = os.environ.get("MONGO_USER")
PASSWORD = os.environ.get("PSWD")

def get_mongo_scrape_db():
    return MongoClient("localhost", 27017, username=USER, password=PASSWORD).scrape

class MongoCollection(str,Enum):
    HomeSearch = "homeSearch"
    PublicDistance = "publicDistance"

def upload_to_mongo(data:List[Tuple], collection):
    client = get_mongo_scrape_db()
    db = client[collection]
    db.insert_many(data)