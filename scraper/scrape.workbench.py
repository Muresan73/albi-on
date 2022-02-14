#%%

from collections import namedtuple
import json
from typing import List
from result import Ok, Err, Result

import plot

from scrape import HousePageInfo
from mongo_utils import get_mongo_scrape_db,MongoCollection,db_distance_info,db_info
from utils import LocationInfo


def test_get_housing_data_at(page: int = 0) -> Result[HousePageInfo, str]:
    offset = page * 50

    with open("test_data/response1.json") as file:
        raw = json.load(file)
        match raw:
            case {
                "data": {
                    "homeSearch": {
                        "filterHomesOffset": {"pagesCount": pagecount, "nodes": data}
                    }
                }
            }:
                return Ok(HousePageInfo(pagecount, page, data))
    return Err("Data not valid")


def test_get_distance_data() -> Result[List[LocationInfo], str]:
    def get_info(raw) -> Result[LocationInfo, str]:
        match raw:
            case {
                "rent": cost,
                "latitude": lat,
                "longitude": lon,
            }:
                return Ok(LocationInfo(float(lat), abs(float(lon)), int(cost)))
        return Err("data is corrupt")

    with open("test_data/response_geo.json") as file:
        raw = json.load(file)
        match raw:
            case {"data": {"homeSearchCoords": {"filterHomesRaw": raw}}}:
                return Ok([get_info(data).unwrap() for data in raw])
    return Err("Data not valid")


def test_distance_data():
    with open("test_data/response-gmaps-distance.json") as file:
        raw = json.load(file)
        # db_insert_distance(raw)

                # %%


def db_info():
    client = get_mongo_scrape_db()
    database = client[MongoCollection.HomeSearch]
    response = database.find(
        {}, {"location": {"latitude": 1, "longitude": 1}, "rent": 1}
    )
    return [
            {
                "lat":item["location"]["latitude"],
                "lon":item["location"]["longitude"],
                "price":item["rent"],
                "id":11,
            }
            for item in response
        ]
    


# plot_data(test_get_distance_data().unwrap())

# plot.distance_region(db_distance_info())
# # %%
plot.price_data(db_info())
# # %%


# # %%
# db = get_mongo_scrape_db()["test"]
# db.update_one({"id": "354974"}, {"$set": {"distance": 12}})
# print(db.find_one({"id": "354974"}, {"id": 1, "distance": 1}))
