'''
INCLUDE THIS IF RUNNING VIA
flask run (or, through compile.sh)
'''



# Imports
import flask
from __init__ import app, SHELFY_BASE_PATH
import os
from werkzeug.utils import secure_filename    # Needed for image upload
import sys




# Register view blueprints
sys.path.append(SHELFY_BASE_PATH)
sys.path.append(SHELFY_BASE_PATH)
import views
app.register_blueprint(views.views)



if __name__ == 'main':
    app.run(host='0.0.0.0', port=80)
