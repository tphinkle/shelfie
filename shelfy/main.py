'''
INCLUDE THIS IF RUNNING VIA
flask run (or, through compile.sh)
'''



# Imports
import flask
import __init__#app, SHELFY_BASE_PATH
import os
from werkzeug.utils import secure_filename    # Needed for image upload
import sys




# Register view blueprints
sys.path.append(__init__.SHELFY_BASE_PATH)
import views
__init__.app.register_blueprint(views.views)



if __name__ == '__main__':
    __init__.app.run()
