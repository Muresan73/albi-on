from collections import namedtuple
from enum import Enum
import os
from typing import List, Union, cast
import pymongo
from dataclasses import asdict, is_dataclass
from utils import helper
from pandas import json_normalize

USER = os.environ.get("MONGO_USER")
PASSWORD = os.environ.get("PSWD")

DBInfo = namedtuple("db_info", ["lat", "lon", "price", "id"])


def get_mongo_scrape_db():
    return pymongo.MongoClient(
        "localhost", 27017, username=USER, password=PASSWORD
    ).scrape


class MongoCollection(str, Enum):
    HomeSearch = "homeSearch"
    PublicDistance = "publicDistance"


def upload_to_mongo(data, collection):
    client = get_mongo_scrape_db()
    db = client[collection]
    if is_dataclass(data):
        data = [asdict(a) for a in data]
    db.insert_many(data)


def db_info() -> List[Union[helper.LocationInfo, helper.LocationWithId]]:
    client = get_mongo_scrape_db()
    database = client[MongoCollection.HomeSearch]
    response = database.find(
        {}, {"location": {"latitude": 1, "longitude": 1}, "rent": 1}
    )
    return cast(
        List[Union[helper.LocationInfo, helper.LocationWithId]],
        [
            DBInfo(
                item["location"]["latitude"],
                item["location"]["longitude"],
                item["rent"],
                item["_id"],
            )
            for item in response
        ],
    )

def db_distance_info():
    client = get_mongo_scrape_db()
    database = client[MongoCollection.PublicDistance]
    response = database.find({})
    return list(response)

def db_distance_info_sanitized():
    sanitized = db_distance_info()
    json_normalize(sanitized)
    return json_normalize(sanitized)