"""Models and database functions for plants db."""


from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry


db = SQLAlchemy()


##############################################################################
#Define tables:

class Observation(db.Model):
    """observation model."""

    __tablename__ = "observations"

    obs_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    # plant_name = db.Column(db.String(150), nullable=False)
    lat = db.Column(db.Float, nullable=False) 
    lon = db.Column(db.Float, nullable=False)
    elev = db.Column(db.Float, nullable=True)
    obs_date = db.Column(db.DateTime, nullable=True)

    plant = db.relationship("Plant", backref="observations")


    def __repr__(self):
        return f"<Observation of {self.plant.sci_name} at ({self.lat}, {self.lon}) on {self.obs_date if self.obs_date else '(Unknown)'}>"


class Plant(db.Model):
    """docstring for Plant"""

    __tablename__ = "plants"

    #BASICS#
    plant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sci_name = db.Column(db.String(150), nullable=False)#str
    toxicity_bool = db.Column(db.Boolean, nullable=False )#bool
    toxicity_notes = db.Column(db.String(150), nullable=True )#str #toxicity fata only shows up on the taxon report, and only if it *is* toxic 
    rare = db.Column(db.Boolean, nullable=False )#bool
    native = db.Column(db.Boolean, nullable=False )#boolean
    bloom_begin = db.Column(db.Integer, nullable=True )#a month was previously a datetime, but that is larger without adding info, since it only contained a month
    bloom_end = db.Column(db.Integer, nullable=True )#a month was previously a datetime, but that is larger without adding info, since it only contained a month
    verbose_desc = db.Column(db.String(1000), nullable=True)#str. from calscape
    technical_desc = db.Column(db.String(1000), nullable=True )#str. from Jepson eFlora

    #URLs#
    calphotos_url = db.Column(db.String(150), nullable=True )#str
    characteristics_url = db.Column(db.String(150), nullable=False )#str
    jepson_url = db.Column(db.String(150), nullable=True )#str
    calscape_url = db.Column(db.String(150), nullable=False )#str
    usda_plants_url = db.Column(db.String(150), nullable=True )#str
    cnps_rare_url = db.Column(db.String(150), nullable=True )#str

    #from CALSCAPE#
    plant_type = db.Column(db.String(50), nullable=False )#str
    min_height = db.Column(db.Float, nullable=True )
    max_height = db.Column(db.Float, nullable=True )
    plant_shape = db.Column(db.ARRAY(db.String(20)), nullable=True)
    flower_color = db.Column(db.ARRAY(db.String(20)), nullable=True)



    def __repr__(self):
        nativeness = "Native" if self.native else "Non-native"
        return f"<{nativeness} plant with ID {self.plant_id} ({self.sci_name})>"
        

class AltName(db.Model):
    """docstring for AltNames"""

    __tablename__ = "alternate_names"

    record_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    name = db.Column(db.String(150), nullable=False)#str. includes both deprecated scientific names and common names

    plant = db.relationship("Plant", backref="alternate")

    def __repr__(self):
        return f"<Record {self.record_num}: {self.plant.sci_name} may also be called {self.name}>"
        


class DistPoly(db.Model):
    """Initialize a table to hold polygonal representations of the distribution of observations."""
    
    __tablename__ = "distribution_polygons"

    poly_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    poly = db.Column(Geometry(geometry_type='POLYGON'))

    plant = db.relationship("Plant", backref="polygon")

    def __repr__(self):
        return f"<Polygon describing observations of {self.plant.sci_name}>"
        

class Trail(db.Model):
    """docstring for Trail"""
    
    __tablename__ = "trails"

    trail_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(300), nullable=True) #some trails are unnamed, I guess
    path = db.Column(Geometry(geometry_type='LINESTRING'), nullable = False)
    trailhead = db.Column(Geometry(geometry_type='POINT'), nullable=False)

    def __repr__(self):
        unnamed = "unnamed"
        return f"<The {self.name if self.name else unnamed} trail with trailhead at {self.trailhead}>"
        

##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///plants'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    init_app()
