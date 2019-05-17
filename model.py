"""Models and database functions for plants db."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##############################################################################
#Define tables:

class Observation(db.Model):
    """observation model."""

    __tablename__ = "observations"

    obs_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer)#, db.ForeignKey('plants.plant_id'))
    plant_name = db.Column(db.String(150), nullable=False)
    lat = db.Column(db.Float, nullable=False) 
    lon = db.Column(db.Float, nullable=False)
    elev = db.Column(db.Float, nullable=True)
    obs_date = db.Column(db.DateTime, nullable=True)

    # plant = db.relationship("Plant", backref="observations")


    def __repr__(self):
        return f"<Observation of {self.plant_name} at ({self.lat}, {self.lon}) on {self.date if self.date else '(Unknown)'}>"


class Plant(db.Model):
    """docstring for Plant"""

    __tablename__ = "plants"

    #BASICS
    plant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sci_name = #str
    toxicity_bool = #bool
    toxicity_notes = #str #toxicity fata only shows up on the taxon report, and only if it *is* toxic 
    native = #boolean
    bloom_period = #?? datetime tuple???
    verbose_desc = #str. from calscape
    technical_desc = #str. from Jepson eFlora

    #URLs
    calphotos_url = #str
    characteristics_url = #str
    jepson_url = #str
    calscape_url = #str
    usda_plants_url = #str

    #if TOLERANCES

    #if ASSOCIATED ORGANISMS

    def __repr__(self):
        return f"<>"
        

class AltNames(db.Model):
    """docstring for AltNames"""

    __tablename__ = "alternate names"

    record_num = #int, primary key
    plant_id = #int, foreign key
    other_name = #str. includes both deprecated scientific names and common names

        
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
