from server import app
from model import Observation, DistPoly, connect_to_db, db 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

connect_to_db(app)
db.create_all()