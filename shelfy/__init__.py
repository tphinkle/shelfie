# Imports
import flask
import os
from werkzeug.utils import secure_filename    # Needed for image upload


# Flask location


# Total hack to get the base path
SHELFY_BASE_PATH = os.path.dirname(__file__)
print('SHELFY BASE PATH', SHELFY_BASE_PATH)




# Configure app
app = flask.Flask(__name__)





app.config.from_object(__name__) # Load config from thsie file (permit_generator.py)

app.config.update(dict(
SECRET_KEY = 'key',
USERNAME = 'admin',
PASSWORD = 'default'
))





# Register view blueprints
import shelfy.views


app.register_blueprint(shelfy.views.views)
