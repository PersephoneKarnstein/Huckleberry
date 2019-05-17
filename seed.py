# from datetime import datetime as dt
from sqlalchemy import func

from model import Observation, connect_to_db, db, init_app
from server import app
from selenium_associate_elevations import get_elevation
import CalFlora_post_request


def get_observations(key_num):
    """Load observations from CalFlora and National Map into database."""

    observations = CalFlora_post_request.obs_to_dict(scientific_name)
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

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    for i in range(1,10):
        get_observations(i)
