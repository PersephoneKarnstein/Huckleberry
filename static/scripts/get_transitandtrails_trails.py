import requests, ast, shapely, geoalchemy2, re
from bs4 import BeautifulSoup
from tqdm import tqdm
import numpy as np
from shapely.geometry import LineString

from model import Trail


def get_trail(trip_num):
    r = requests.get(f"https://www.transitandtrails.org/trips/{trip_num}")
    soup = BeautifulSoup(r.content)

    if soup.h2.get_text(strip=True) == 'Page Not Found (404)':
        return None

    else:
        route = soup.find("script", string=re.compile("trip_route")).get_text()
        try:
            route = np.asarray(ast.literal_eval(route[14:-2]))[:,::-1] #we get the points in 
            # (lat, lon) order and we need them in (lon, lat) order
        except IndexError: return None #basically this means that we expected to find a trail but didn't

        shapely_route = shapely.geometry.LineString(route)
        geoalchemy_route = geoalchemy2.shape.from_shape(shapely_route, srid=4326)

        hikename = soup.select_one("#trip-meta > div.header > h2").get_text()

        try:
            trailhead_link = "https://www.transitandtrails.org" + \
                soup.select_one(".trailhead").find("a", "trailhead")["href"] + ".json"

            trailhead = requests.get(trailhead_link).json()
            trailhead_point = geoalchemy2.elements.WKTElement(\
                f'POINT({trailhead["longitude"]} {trailhead["latitude"]})', srid=4326)
        except TypeError: #apparently sometimes it doesn't know the trailhead.
            trailhead_point = geoalchemy2.elements.WKTElement(\
                f'POINT({route[0][0]} {route[0][1]})', srid=4326) #in this case 
            # we just guess (bc this is bb trails just for proof of concept sake)
            # that the trailhead is the first point returned by the 'route' 

        trail = Trail(name=hikename,
                        path=geoalchemy_route,
                        trailhead=trailhead_point)

        return trail

