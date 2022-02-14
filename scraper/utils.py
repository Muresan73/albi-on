from collections import namedtuple
from dataclasses import dataclass
from typing import Any
@dataclass
class Location(object):
    lat:float
    lon:float
@dataclass
class LocationWithId(Location):
    id:Any
@dataclass
class LocationInfo(Location):
    price:int

@dataclass
class Distance:
    origin:Location
    target: Location
    distance_time: int

split_array = lambda array,n:[array[i:i + n] for i in range(0, len(array), n)]

extract_location = lambda o:Location(o.lat,o.lon)

# namedtuple("Fszom",["origin", "target", "distance"])