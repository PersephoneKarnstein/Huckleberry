from jinja2 import StrictUndefined

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from static.scripts.model import *
from sqlalchemy import func
from shapely.geometry import Point, Polygon
import os
import numpy as np

from flask import Flask, request, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension

# from static.scripts.model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("bootstrap.html")


@app.route("/get-trails.json", methods=["POST"])
def get_trails():
    mapbounds = request.get_json()
    # print(mapbounds, request.args, "\n\n\n\n\n\n\n")
    ne, nw, sw, se = [[mapbounds["north"], mapbounds["east"]], [mapbounds["north"], mapbounds["west"]], [mapbounds["south"], mapbounds["west"]], [mapbounds["south"], mapbounds["east"]]]
    poly = Polygon([n[::-1] for n in [ne, nw, sw, se]]) #because we store it in postGIS with longitude first, remember.
    viewbox = from_shape(poly, srid=4326)
    visible_trails = dict()

    all_trails = db.session.query(Trail).filter(Trail.path.ST_Intersects(viewbox)).all()
    for trail in all_trails:
        visible_trails[trail.trail_num] = dict()
        trail_points = np.asarray(to_shape(trail.path).xy).T
        visible_trails[trail.trail_num]["path"] = \
            [{"lat":float(x[1]), "lng":float(x[0])} for x in trail_points]

        visible_trails[trail.trail_num]["name"] = trail.name
        print("\n\n\n", (to_shape(trail.trailhead).xy[0])[0], type((to_shape(trail.trailhead).xy[0])[0]), "\n\n\n")
        visible_trails[trail.trail_num]["trailhead"] = \
            {"lat":(to_shape(trail.trailhead).xy[1])[0], "lng":(to_shape(trail.trailhead).xy[0])[0]}

    print(jsonify(visible_trails))
    return jsonify(visible_trails)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
