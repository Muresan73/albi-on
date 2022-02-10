#%%

from collections import namedtuple
import json
from typing import List
from result import Ok, Err, Result

import plot
from fill_geo_data import db_info,LocationInfo

from scrape import HousePageInfo


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
    def get_info(raw) -> Result[LocationInfo,str]:
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
# %%

# plot_data(test_get_distance_data().unwrap())

# %%
plot.price_data(db_info())


# %%
db = get_mongo_scrape_db()['test']
db.update_one({"id":'354974'},{"$set":{"distance":12}})
print(db.find_one({"id":'354974'},{"id":1,"distance":1}))
