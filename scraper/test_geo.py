import json
from unittest.mock import Mock
from urllib import response
import pytest
import requests
import mongo_utils

from fill_geo_data import upload_distances_to_T_C
from mongo_utils import MongoCollection
from utils import Location


@pytest.fixture(autouse=True)
def default_parameters(monkeypatch):
    monkeypatch.delattr("requests.get")
    monkeypatch.setenv("MONGO_USER", "db")
    monkeypatch.setenv("PSWD", "pswd")
    monkeypatch.setenv("APIKEY", "4-xy")
    monkeypatch.setenv("ENDPOINT", "https://api.url.se/graphql")

class MockResponse:
    def __init__(self,response) -> None:
        self.response = response
    @property
    def text(self):
        return self.response


def test_google_distance_data_upload(monkeypatch):

    with open("test_data/db_info.json") as dbfile:
        dictlist = json.load(dbfile)
        info = [mongo_utils.DBInfo(**dictionary) for dictionary in  dictlist ]
        
        with open("test_data/response-gmaps-distance.json") as file:
            raw = file.read()
            monkeypatch.setattr(requests, "request", lambda *_,**__:MockResponse(raw))
            monkeypatch.setattr(mongo_utils, "db_info", lambda:info)
            mock = Mock()
            first_values_sample = []
            mock.side_effect = lambda x,collection:  first_values_sample.append(
                 (collection,x[0].origin,x[0].target,x[0].distance_time,len(x))
                 )
            monkeypatch.setattr(mongo_utils, "upload_to_mongo", mock)
            upload_distances_to_T_C()

            collection, origin, target, distance, size = first_values_sample[0]
            assert collection == MongoCollection.PublicDistance
            assert origin == Location(lat=59.3356075465, lon=18.0353782334)
            assert target ==  Location(lat=59.330767, lon=18.0591)
            assert distance ==  480
            assert size == 10
            
            collection, origin, target, distance, size = first_values_sample[1]
            assert collection == MongoCollection.PublicDistance
            # assert origin == Location(lat=59.3545363, lon=17.8831046)
            # assert target ==  Location(lat=59.330767, lon=18.0591)
            assert distance ==  480
            assert size == 10

            collection, origin, target, distance, size = first_values_sample[2]
            assert collection == MongoCollection.PublicDistance
            # assert origin == Location(lat=59.3627004, lon=17.8390893)
            # assert target ==  Location(lat=59.330767, lon=18.0591)
            assert distance ==  480
            assert size == 10

            mock.assert_called()

def test_error_on_response(monkeypatch):
    with open("test_data/db_info.json") as dbfile:
        dictlist = json.load(dbfile)
        info = [mongo_utils.DBInfo(**dictionary) for dictionary in  dictlist ]
        
        with open("test_data/response-gmaps-distance.json") as file:
            raw = json.load(file)
            raw['rows'] = raw['rows'][:10]
            monkeypatch.setattr(requests, "request", lambda *_,**__:MockResponse(raw))
            monkeypatch.setattr(mongo_utils, "db_info", lambda:info)
            monkeypatch.delattr(mongo_utils, "upload_to_mongo")

            with pytest.raises(Exception) as e:
                upload_distances_to_T_C()
                assert e == Exception("Number of locations and response size mismatch") 

def test_upload(monkeypatch):
    with open("test_data/db_info.json") as dbfile:
        dictlist = json.load(dbfile)
        info = [mongo_utils.DBInfo(**dictionary) for dictionary in  dictlist ]
        
        with open("test_data/response-gmaps-distance.json") as file:
            raw = json.load(file)
            raw['rows'] = raw['rows'][:10]
            monkeypatch.setattr(requests, "request", lambda *_,**__:MockResponse(raw))
            monkeypatch.setattr(mongo_utils, "db_info", lambda:info)
            # monkeypatch.delattr(mongo_utils, "upload_to_mongo")

            upload_distances_to_T_C()

