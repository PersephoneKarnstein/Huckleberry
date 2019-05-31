# from datetime import datetime as dt
# from sqlalchemy import func
from tqdm import tqdm, tqdm_gui
import os, sys

from model import Observation, Plant, AltName, connect_to_db, db
from server import app
from selenium_associate_elevations import get_elevation

import CalFlora_post_request
from collect_plant_data import get_plant_taxon_report, get_plant_data_calscape

from get_transitandtrails_trails import get_trail

startfrom = (int(sys.argv[1]) if len(sys.argv)>1 else 0)
print(startfrom)

def get_observations(scientific_name, plant_id):
    """Load observations from CalFlora and National Map into database."""

    observations = CalFlora_post_request.obs_to_dict(scientific_name, plant_id)
    obs_this_plant = len(observations)

    obs_read = tqdm(total=obs_this_plant, desc="Starting Up...", unit="obs", miniters=5)
    # pbar.reset()
    pbar_desc = (scientific_name[:30] + '..') if len(scientific_name) > 30 else scientific_name
    obs_read.set_description('\x1b[6;30;42m' +pbar_desc+ '\x1b[0m')


    for j, observation in enumerate(observations):
        # elevation = get_elevation(observation["lat"], observation["lon"])
        # observation["elev"] = elevation
        observation["elev"] = None #until I rewrite the elevation request to do multiple locations at once to decrease costs.

        obs = Observation(plant_id=observation["plant_id"],
                            # plant_name=observation["plant_name"],
                            lat=observation["lat"],
                            lon=observation["lon"],
                            elev=observation["elev"],
                            obs_date=observation["obs_date"])

        
        # plant = Plant(plant)
        # We need to add to the session or it won't ever be stored
        db.session.add(obs)

        # provide some sense of progress
        # if i % 100 == 0:
        # print(f"{i}:{j}/{obs_this_plant}\n{obs.plant_name}\n({obs.lat},{obs.lon})")
        # if obs.obs_date:
        #     print(f"{obs.obs_date.strftime('%m/%d/%Y')}\n\n")

        obs_read.update(1)
        # Once we're done, we should commit our work
    db.session.commit()
    obs_read.close()


def get_plant_data(key_number, pbar1=None):
    plant_data, alternate_names = get_plant_taxon_report(key_number)
    if plant_data is not None:
        plant_data = get_plant_data_calscape(plant_data)

        plant = Plant(plant_id=key_number,
                    sci_name=plant_data["sci_name"],
                    plant_type=plant_data["plant_type"],
                    min_height=plant_data["min_height"],
                    max_height=plant_data["max_height"],
                    plant_shape = plant_data["plant_shape"],
                    flower_color=plant_data["flower_color"],
                    toxicity_bool=plant_data["toxicity_bool"],
                    toxicity_notes=plant_data["toxicity_notes"],
                    native=plant_data["native"],
                    rare=plant_data["rare"],
                    bloom_begin=plant_data["bloom_begin"],
                    bloom_end=plant_data["bloom_end"],
                    verbose_desc=plant_data["verbose_desc"],
                    technical_desc=plant_data["technical_desc"],
                    calphotos_url=plant_data["calphotos_url"],
                    characteristics_url=plant_data["characteristics_url"],
                    jepson_url=plant_data["jepson_url"],
                    calscape_url=plant_data["calscape_url"],
                    usda_plants_url=plant_data["usda_plants_url"],
                    cnps_rare_url=plant_data["cnps_rare_url"])

        # print(plant)
        db.session.add(plant)
        
        for name in alternate_names:
            altname = AltName(plant_id=key_number, name=name)
            db.session.add(altname)

        db.session.commit()

        get_observations(plant_data["sci_name"], plant_data["plant_id"])
    else: pass


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    # plants_fetched = tqdm_gui(total=13000, initial=startfrom)

    i=startfrom
    while True:
        print(f"\rSearching trail {i}")
        trail = get_trail(i)
        if trail is not None:
            db.session.add(trail)
            db.session.commit()
        else: pass
        # get_plant_data(i)
        # plants_fetched.update(1)
        # if i%10 ==0:
        #     os.system("pg_dump plants | gzip > plants.gz")
        i+=1

    # plants_fetched.close()