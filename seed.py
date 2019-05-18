# from datetime import datetime as dt
from sqlalchemy import func

from model import Observation, Plant, connect_to_db, db, init_app
from server import app
from selenium_associate_elevations import get_elevation

import CalFlora_post_request
from collect_plant_data import get_plant_taxon_report

def get_observations(scientific_name, plant_id):
    """Load observations from CalFlora and National Map into database."""

    observations = CalFlora_post_request.obs_to_dict(scientific_name, plant_id)
    obs_this_plant = len(observations)
    for j, observation in enumerate(observations):
        elevation = get_elevation(observation["lat"], observation["lon"])
        observation["elev"] = elevation

        obs = Observation(plant_id=observation["plant_id"],
                            plant_name=observation["plant_name"],
                            lat=observation["lat"],
                            lon=observation["lon"],
                            elev=observation["elev"],
                            obs_date=observation["obs_date"])

        
        # plant = Plant(plant)
        # We need to add to the session or it won't ever be stored
        db.session.add(obs)

        # provide some sense of progress
        # if i % 100 == 0:
        print(f"{i}:{j}/{obs_this_plant}\n{obs.plant_name}\n({obs.lat},{obs.lon})")
        if obs.obs_date:
            print(f"{obs.obs_date.strftime('%m/%d/%Y')}\n\n")

        # Once we're done, we should commit our work
        db.session.commit()



def get_plant_data(key_number):
    plant_data, alternate_names = get_plant_taxon_report(key_number)

    plant = Plant(plant_id=key_number,
        sci_name=plant_data["sci_name"],
        toxicity_bool=plant_data["toxicity_bool"],
        toxicity_notes=plant_data["toxicity_notes"],
        rare=plant_data["rare"],
        native=plant_data["native"],
        verbose_desc=plant_data["verbose_desc"],
        technical_desc=plant_data["technical_desc"],
        calphotos_url=plant_data["calphotos_url"],
        characteristics_url=plant_data["characteristics_url"],
        jepson_url=plant_data["jepson_url"],
        calscape_url=plant_data["calscape_url"],
        usda_plants_url=plant_data["usda_plants_url"],
        cnps_rare_url=plant_data["cnps_rare_url"])

    print(plant)
    db.session.add(plant)
    db.session.commit()

    get_observations(plant_data["sci_name"], plant_data["plant_id"])



if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    for i in range(1,10):
        get_plant_data(i)