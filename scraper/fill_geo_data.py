from collections import namedtuple
import os
from typing import List
import requests
from  urllib.parse import urlencode
from utils import MongoCollection, get_mongo_scrape_db
import plot


LocationInfo = namedtuple("Location_info", ["lat", "lon", "price"])
Location = namedtuple("Location", ["lat", "lon"])


def get_distance(locations:List[LocationInfo],target=Location(59.330767, 18.059100)):
    get_location_string = lambda location:"{},{}".format(location.lat,location.lon)
    APIKEY = os.environ.get("APIKEY")
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    origins = '|'.join([get_location_string(item) for item in locations])
    
    destinations = '|'.join([get_location_string(target)]*len(locations))


    params = {'origins': origins, 'destinations': destinations,'key':APIKEY}
    payload = {}
    headers = {}

    response = requests.request("GET", url + urlencode(params), headers=headers, data=payload)
    print(response.text)

def db_info()->List[LocationInfo]:
    client = get_mongo_scrape_db()
    database = client[MongoCollection.HomeSearch]
    response = database.find({},{"location":{"latitude":1,"longitude":1},"rent":1})
    return [LocationInfo(item['location']['latitude'],item['location']['longitude'],item['rent']) for item in response]
    








if __name__ == "__main__":
    # plot_data()
    plot.price_data(db_info())
    # get_distance(db_info()[:150])
    # get_distance(db_info()[:10])
