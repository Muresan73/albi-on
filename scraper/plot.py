from typing import List
import pandas as pd

from fill_geo_data import LocationInfo


def price_data(data: List[LocationInfo]):
    df = pd.DataFrame(data)
    import plotly.express as px

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

def distance_region(data: List[LocationInfo]):
    pass