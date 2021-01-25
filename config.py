import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the scripts runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:farhanmadka@localhost:5432/myfyyur_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
