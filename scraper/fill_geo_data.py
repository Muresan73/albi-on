import os
from typing import List, Any
import requests
from urllib.parse import urlencode
import mongo_utils
from utils import Distance
from utils import Location, split_array, extract_location
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.model_selection import learning_curve
from sklearn.model_selection import validation_curve
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def get_distance(locations: List[Location], targets: List[Location]):
    def get_duration(data):
        return data["duration"]["value"] if "duration" in data else None

    def get_values(data) -> List[int|None]:
        match data:
            case {"rows": nodes}:
                return [get_duration(item["elements"][0]) for item in nodes]
        return []

    APIKEY = os.environ.get("APIKEY")
    if not APIKEY:
        return None

    get_location_string = lambda location: "{},{}".format(location.lat, location.lon)
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    origins = "|".join([get_location_string(item) for item in locations])
    destinations = "|".join([get_location_string(item) for item in targets])

    params = {
        "origins": origins,
        "destinations": destinations,
        "mode": "transit",
        "key": APIKEY,
    }
    payload = {}
    headers = {}

    response = requests.request(
        "GET", url + urlencode(params), headers=headers, data=payload
    )

    response_json = json.loads(response.text)
    values = get_values(response_json)

    return values


def upload_distances_to_T_C():
    STEP = 10
    default_target = [Location(59.330767, 18.059100)] * STEP
    locations: Any = mongo_utils.db_info()
    partitions = split_array(locations, STEP)
    for part in partitions:
        values = get_distance(part, default_target) or []
        if len(part) > len(values):
            raise Exception("Number of locations and response size mismatch")
        data = [
            Distance(
                extract_location(origin),
                extract_location(target),
                distance,
            )
            for origin, target, distance in zip(part, default_target, values)
            if distance is not None
        ]
        mongo_utils.upload_to_mongo(data, mongo_utils.MongoCollection.PublicDistance)


def distance_linear_regression():
    normalized = mongo_utils.db_distance_info_sanitized()
    df = pd.DataFrame(normalized)

    X = df.loc[:, ~df.columns.isin(['_id', 'distance_time'])]
    y = df['distance_time']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
    # reg = ElasticNet()
    # reg.fit(X_train, y_train)
    poly_reg = PolynomialFeatures(2)
    X_poly = poly_reg.fit_transform(X)
    lin_reg = LinearRegression()
    lin_reg.fit(X_poly,y)
    scores = cross_val_score(lin_reg, X, y)
    print('CV accuracy: %.3f +/- %.3f' % (np.mean(scores), np.std(scores)))

    y_range = lin_reg.predict(X_poly)
    import plotly.express as px
    import plotly.graph_objects as go

    fit_range = pd.DataFrame(zip(X['origin.lat'],y_range),columns =['lat', 'fit'])
    fit_range = fit_range.sort_values(by=['lat'])
    fig = px.scatter(X, x='origin.lat', y=y, opacity=0.65)
    fig.add_traces(go.Scatter(x=fit_range.lat, y=fit_range.fit, name='Regression Fit'))
    fig.show()


if __name__ == "__main__":
    # upload_distances_to_T_C()

    distance_linear_regression()
    # import plotly.express as px
    # fig = px.scatter(x=df['origin.lat'], y=df.distance_time,color_discrete_sequence=['red'])
    # fig = px.scatter(x=df['origin.lon'], y=df.distance_time,color_discrete_sequence=['blue'])
    # fig.show()
    # import plotly.graph_objects as go
    # fig = go.Figure(data =
    # go.Contour(
    #     z=df['distance_time'],
    #     x=df['origin.lat'],
    #     y=df['origin.lon']
    # ))
    # fig.show()
