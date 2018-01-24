# Imports
import os

import flask

# Base path for project
SHELFY_BASE_PATH = os.path.dirname(__file__)




# Configure app
app = flask.Flask(__name__)





app.config.from_object(__name__) # Load config from thsie file (permit_generator.py)

app.config.update(dict(
SECRET_KEY = 'key',
USERNAME = 'admin',
PASSWORD = 'default'
))
