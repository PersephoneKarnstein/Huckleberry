from server import app
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from model import *
from sqlalchemy import func
from shapely.geometry import Point, Polygon

init_app()

# cat = db.session.query(DistPoly).filter(DistPoly.poly.ST_Intersects('SRID=4326;POINT(-122.4124033 37.7836467)')).all()
# aaa = set([a.plant.sci_name for a in cat])
# set([a.plant.sci_name for a in db.session.query(DistPoly).filter(DistPoly.poly.ST_Intersects(trail.path)).all()])


poly = Polygon([n[::-1] for n in [ne, a, sw, b]]) #becayse we store the hash with longitude first, remember.
viewbox = from_shape(poly, srid=4326)

cat2 = db.session.query(Trail).filter(Trail.path.ST_Intersects(viewbox)).first()
la = np.asarray(to_shape(cat2.path).xy).T
pretend_jquery = ", ".join("{"+f"lat: {a[1]}, lng: {a[0]}"+"}" for a in la)

===> put that into javascript as a variable, send that to google as a polyline