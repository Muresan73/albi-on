from typing import List
import pandas as pd

from utils import LocationInfo
import plotly.express as px


def price_data(data: List[LocationInfo]):
    df = pd.DataFrame(data)

    fig = px.scatter_mapbox(
        df,
        title = 'House Prices',
        lat=df.lat,
        lon=df.lon,
        color="price",  # which column to use to set the color of markers
        range_color=[8000,20000],
        mapbox_style="carto-darkmatter",
        # mapbox_style="carto-positron",
        color_continuous_scale=["gold","orangered" ,"#550055"],
        center={'lat':59.31, 'lon':18.06},
        zoom=11,
    )
    return fig.show()

def distance_region(data):
    lat = [item['origin']["lat"] for item in data]
    lon = [item['origin']["lon"] for item in data]
    distance_time = [round(item['distance_time']/60,ndigits=1) for item in data]
    fig = px.scatter_mapbox(
        title = 'Public Transport From T-Centralen',
        lat=lat,
        lon=lon,
        color=distance_time,
        range_color=[0,40],
        mapbox_style="carto-darkmatter",
        # mapbox_style="carto-positron",
        color_continuous_scale=["Lime","gold","orangered"],
        labels={ 'color':'time'},
        center={'lat':59.31, 'lon':18.06},
        zoom=11,
    )
    return fig.show()