#We have 1x1 degree blocks of xyz data stored in /elevation/
#e.g.
#n33w114.txt
#   `->   -114.00152777781112 33.0015277777752445 557.18670654296875
#         -114.001250000033338 33.0015277777752445 541.68731689453125
#         -114.000972222255555 33.0015277777752445 523.91448974609375
#
#we want to take a lat/lon from our observation and associate an elevation with it.

from CalFlora_post_request import *

import numpy as np

def build_elev_filename(obs_lat, obs_lon):
    """This is technically unnecessary since all the 1-degree blocks of elevations we're
    looking at fall within the NW quadrant, but that seems dishonest"""
    elev_filename = "elevation/"

    elev_filename += ("n" if obs_lat > 0 else "s")

    elev_filename += str(int(abs(np.floor(obs_lat)+1)))

    elev_filename += ("e" if obs_lon > 0 else "w")

    elev_filename += str(int(abs(np.ceil(obs_lon)-1))) + ".txt"

    print(elev_filename)
    return elev_filename


def associate_elevation(obs_dict):
    print(obs_dict)
    lat, lon = obs_dict["lat"], obs_dict["lon"]
    lat_precision, lon_precision = (len(repr(a).split('.')[-1]) for a in [lat, lon])

    with open(build_elev_filename(lat, lon)) as f:
        elev_measurements, elev_weights = [], []
       
        for line in f:
            file_lat, file_lon = float(line.split()[1]), float(line.split()[0])
            rounding_precision = (int(np.mean([lat_precision, lon_precision]))-2 if np.mean([lat_precision, lon_precision])>2 else 0)
       
            if (round(file_lat, rounding_precision) == round(lat, rounding_precision)) and \
            (round(file_lon, rounding_precision) == round(lon, rounding_precision)):
       
                elev_measurements.append(float(line.split()[2]))
                elev_dist = np.sqrt((file_lat-lat)**2 + (file_lon-lon)**2)
                elev_weights.append(1./(1.+elev_dist))
       
            else: pass

        # print(elev_measurements)
        avg_elev = np.average(elev_measurements, weights=elev_weights)
        weighted_std_elev = np.sqrt(np.average((elev_measurements-avg_elev)**2, weights=elev_weights))

        print(f"n={len(elev_measurements)}; mean={avg_elev}; sigma={weighted_std_elev}")





key_number = 1
data = compose_request(key_number)
plant_name, extracted = process_request_results(data)
obs_dict = {"plant_id":key_number, "plant_name":plant_name, "lat":float(extracted[3][1]), "lon":float(extracted[3][0]), "elev":None, "obs_date":extracted[3][2]}


associate_elevation(obs_dict)
