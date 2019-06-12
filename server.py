from jinja2 import StrictUndefined

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from static.scripts.model import *
from static.scripts.inaturalist_handler import get_inat_obs
from sqlalchemy import func
from sqlalchemy.orm.collections import InstrumentedList
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.validation import explain_validity
import os, random, shapely
import numpy as np

from flask import Flask, request, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from bs4 import BeautifulSoup
import requests, urllib, ast, re, json


# from static.scripts.model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


def viewbox_to_poly(mapbounds={"south": 37.7425615445232, "west": -122.63350323076173, "north": 37.8892913099587, "east": -121.97432354326173}):
    ne, nw, sw, se = [[mapbounds["north"], mapbounds["east"]], [mapbounds["north"], mapbounds["west"]], [mapbounds["south"], mapbounds["west"]], [mapbounds["south"], mapbounds["east"]]]
    poly = Polygon([n[::-1] for n in [ne, nw, sw, se]]) #because we store it in postGIS with longitude first, remember.
    # viewbox = from_shape(poly, srid=4326)
    return poly

def trails_to_pts(sql_trail_results):
    visible_trails = dict()

    for trail in sql_trail_results:
        visible_trails[trail.trail_num] = dict()
        trail_points = np.asarray(to_shape(trail.path).xy).T
        visible_trails[trail.trail_num]["path"] = \
            [{"lat":float(x[1]), "lng":float(x[0])} for x in trail_points]

        visible_trails[trail.trail_num]["name"] = trail.name
        # print("\n\n\n", (to_shape(trail.trailhead).xy[0])[0], type((to_shape(trail.trailhead).xy[0])[0]), "\n\n\n")
        visible_trails[trail.trail_num]["trailhead"] = \
            {"lat":(to_shape(trail.trailhead).xy[1])[0], "lng":(to_shape(trail.trailhead).xy[0])[0]}

    return visible_trails

def multipolygon_to_xy(poly):
    polygon_bounds = []
    if poly.geom_type == 'MultiPolygon':
        # do multipolygon things.
        polygons = list(poly)
    elif poly.geom_type == 'Polygon':
        polygons = [poly]
    else:
        return []
    for polygon in polygons:
        border_points = np.asarray(polygon.exterior.xy).T
        border = [{"lat":float(x[1]), "lng":float(x[0])} for x in border_points]
        polygon_bounds.append(border)
    print(polygon_bounds)
    return list(polygon_bounds)

def build_card(plant_obj):
    """ build the info card that goes in our sidebar, and embed the data we have on the plant"""

    #first, check if wikipedia has a page and picture for the plant because it will probably be better than just grabbing the first one off calphotos
    photo_options = []
    r = requests.get(f"""https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote((plant_obj.sci_name).replace(" ", "_"))}""")
    if r.status_code != 200:
        nameguess = (plant_obj.sci_name).split(" ssp.")[0].split(" ×")[0].replace(" ", "_")
        r = requests.get(f"""https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(nameguess)}""")

    if r.status_code == 200:
        if "thumbnail" in r.json().keys():
            photo_src = r.json()["thumbnail"]["source"]
        if "originalimage" in r.json().keys():
            photo_options = [r.json()["originalimage"]["source"]]


    page = requests.get(plant_obj.calphotos_url)
    if page:
        soup = BeautifulSoup(page.content, features="lxml")
        photo_options.extend(["https://calphotos.berkeley.edu/"+a.attrs["src"] for a in soup.find_all("img")])
        photo_src = photo_options[0]
    
    if not photo_options:  
        photo_src = "../static/resources/no-picture.png"
        photo_options = [photo_src]
    
    alt_names = plant_obj.alternate
    common_name = (alt_names[0].name if isinstance(alt_names, InstrumentedList) else alt_names.name)

    print(json.dumps(([a.name.replace("'", "!") for a in alt_names])))

    return f"""<div class="row justify-content-left my-2" style="align-items: center;">
        <div class="card bg-light" 
                data-toggle="modal" 
                data-target="#exampleModalCenter" 
                data-plant-id="{plant_obj.plant_id}"
                data-alt-names="{[a.name.replace("'", "!") for a in alt_names]}"
                data-sci-name="{plant_obj.sci_name}"
                data-toxicity-bool="{plant_obj.toxicity_bool}"
                data-toxicity-notes="{plant_obj.toxicity_notes if plant_obj.toxicity_notes else 'none'}"
                data-rare="{plant_obj.rare}"
                data-native="{plant_obj.native}"
                data-bloom-begin="{plant_obj.bloom_begin if plant_obj.bloom_begin else 'none'}"
                data-bloom-end="{plant_obj.bloom_end if plant_obj.bloom_end else 'none'}"
                data-verbose-desc="{(plant_obj.verbose_desc.replace("'", "!") if plant_obj.verbose_desc else 'none')}"
                data-technical-desc="{plant_obj.technical_desc if plant_obj.technical_desc else 'none'}"
                data-calphotos-url="{plant_obj.calphotos_url if plant_obj.calphotos_url else 'none'}"
                data-characteristics-url="{plant_obj.characteristics_url}"
                data-jepson-url="{plant_obj.jepson_url if plant_obj.jepson_url else 'none'}"
                data-calscape-url="{plant_obj.calscape_url}"
                data-usda-plants-url="{plant_obj.usda_plants_url if plant_obj.usda_plants_url else 'none'}"
                data-cnps-rare-url="{plant_obj.cnps_rare_url if plant_obj.cnps_rare_url else 'none'}"
                data-plant-type="{plant_obj.plant_type}"
                data-min-height="{plant_obj.min_height if plant_obj.min_height else 'none'}"
                data-max-height="{plant_obj.max_height if plant_obj.max_height else 'none'}"
                data-plant-shape="{plant_obj.plant_shape if plant_obj.plant_shape else 'none'}"
                data-flower-color="{plant_obj.flower_color if plant_obj.flower_color else 'none'}"
                data-photo-options="{photo_options}"
                style="width: 20rem;" > 
          <div class="card-body">
            <div class="row">
              <div class="col-3" style="padding-right: 0 !important; padding-left: 0 !important;">
                <img src="{photo_src}" alt="plant picture" class="img-thumbnail" >
              </div>
              <div class="col">
                <h6 class="card-title">{common_name}</h6>
                <h7 class="card-title" style="text-shadow: none;"><i>{plant_obj.sci_name}</i></h7>
              </div>
            </div>
          </div>
        </div>
        <div class="col" style="display: flex; align-items: center;">
          <button type="button" class="btn btn-outline-danger">Remove</button>
        </div>
      """



@app.route('/')
def index():
    """Homepage."""

    return render_template("bootstrap.html")


@app.route("/templates/plant-to-hike.html")
def return_plant_to_hike():
    return render_template("plant-to-hike.html")


@app.route("/get-trails.json", methods=["POST"])
def get_trails():
    mapbounds = request.get_json()
    # print(mapbounds, request.args, "\n\n\n\n\n\n\n")
    viewbox = viewbox_to_poly(mapbounds)

    all_trails = db.session.query(Trail).filter(Trail.path.ST_Intersects(viewbox)).all()
    visible_trails = trails_to_pts(all_trails)

    # print(jsonify(visible_trails))
    return jsonify(visible_trails)


@app.route("/get-plants.json", methods=["POST"])
def get_plants():
    """we want to return a list of plants"""
    plant_data = request.get_json()
    mapbounds = plant_data["mapBoundary"]
    # print(mapbounds, request.args, "\n\n\n\n\n\n\n")
    viewbox = viewbox_to_poly(mapbounds)
    
    and_or = plant_data["andOr"]
    other_plants = plant_data["intersectingPlants"]


    visible_plants = set()

    if len(other_plants)==100: 
        search_area = viewbox

    else:
        search_area = viewbox
        for intersecting_plant in other_plants:
            # plant_polys = db.engine.execute(f"SELECT DISTINCT poly FROM distribution_polygons WHERE plant_id = {intersecting_plant};").fetchall()
            plant_polys = db.session.query(DistPoly.poly).filter(DistPoly.plant_id == intersecting_plant).all()
            #returns all the distribution polygons for a given plant ID
            # print(plant_polys)
            if isinstance(plant_polys, list):
                # for plant_poly in plant_polys:
                plant_polys = MultiPolygon([shapely.wkt.loads(to_shape(poly_result.poly).wkt) for poly_result in plant_polys])
                
            else: plant_polys = to_shape(plant_polys.poly)


            if not plant_polys.is_valid:
                print(explain_validity(plant_polys))
                print("the buffered version would(?) be valid: "+str(plant_polys.buffer(0.0).is_valid)) 
                plant_polys = plant_polys.buffer(0.0)
            search_area = search_area.intersection(plant_polys) #modify the search area to only include the places where those they intersect
            print(search_area.area)
            #currently hardcoded to AND operators for plant overlaps, maybe ad OR later


    new_bounding_box = search_area.bounds #returns a 4-ple of (minx, miny, maxx, maxy)
    # print(new_bounding_box)
    search_area_geoalc = from_shape(search_area, srid=4326)
    # print("\n\n\n\n\n\n", new_bounding_box,"\n\n\n\n\n\n")
    all_trails = db.session.query(Trail).filter(Trail.path.ST_Intersects(search_area_geoalc)).all()
    visible_trails = trails_to_pts(all_trails)

    all_plants = {a[0] for a in db.session.query(DistPoly.plant_id).filter(DistPoly.poly.ST_Intersects(search_area_geoalc)).all()}
    visible_plants_sci_names = [a[0] for a in db.session.query(Plant.sci_name).filter(Plant.plant_id.in_(all_plants)).all()]
    visible_plants_alt_names = [a[0] for a in db.session.query(AltName.name).filter(AltName.plant_id.in_(all_plants)).all()]

    print([[a["lng"], a["lat"]] for a in multipolygon_to_xy(search_area)[0]])
    # print(visible_trails[:20], visible_plants_sci_names[:20])
    
    visible_objs = {"new_bounds":{"south":new_bounding_box[0], "west":new_bounding_box[1], "north":new_bounding_box[2], "east":new_bounding_box[3]},
                    "intersection":  multipolygon_to_xy(search_area)[0], #this I probably need to turn into a set of points
                    "visible_trails": visible_trails,
                    "visible_plants": visible_plants_sci_names+visible_plants_alt_names
                    }

    # print(visible_objs["intersection"], search_area)

    # print(jsonify(visible_trails))
    return jsonify(visible_objs)


@app.route("/get-plant-data.json", methods=["POST"])
def get_plant_data():
    plant_name = str(request.data.decode(encoding="utf-8"))
    print(plant_name)
    scis = db.session.query(Plant).filter(Plant.sci_name == plant_name).distinct().all()
    alts = [a.plant for a in db.session.query(AltName).filter(AltName.name == plant_name).distinct().all()] 

    returned_plants = list({*scis, *alts})
    #what if there's more than one thing with that name found?
    #I decree that we want to return the thing with the most observations on the
    #assumption that that was probably what they were looking for
    # print(returned_plants)
    #get number of observations
    plantids = [a.plant_id for a in returned_plants]
    numobs = np.asarray([db.session.query(func.count(Observation.obs_id)).filter(Observation.plant_id==pid).scalar() for pid in plantids])
    numobs += np.asarray([len(get_inat_obs(plant.sci_name)) if get_inat_obs(plant.sci_name) else 0 for plant in returned_plants])


    if len(returned_plants)>1:
        most_popular_plant_tuple = sorted(zip(numobs,returned_plants), key=lambda pair: pair[0])[0]
        most_popular_plant = most_popular_plant_tuple[1]
        num_obs = int(most_popular_plant_tuple[0])
    elif len(returned_plants) == 1: 
        most_popular_plant = returned_plants[0]
        num_obs = int(numobs[0])
    else: 
        print("no plants found")
        return jsonify({})

    plant_data = dict(vars(most_popular_plant)) 
    del(plant_data["_sa_instance_state"])
    plant_data["num_obs"] = num_obs
    plant_data["card_html"] = build_card(most_popular_plant)
    #add the html for the card
    # print(plant_data)
    # for key, datum in dict(vars(most_popular_plant)):
        # if isinstance(datum, np.int64): print(key, datum)

    return jsonify(plant_data)

@app.route("/popover")
def get_cover():
    return "../static/resources/backgrounds/"+random.choice(os.listdir("static/resources/backgrounds"))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
