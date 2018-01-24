'''
INCLUDE THIS IF RUNNING VIA
flask run (or, through compile.sh)
'''



# Imports
import flask
from __init__ import app
import os
from werkzeug.utils import secure_filename    # Needed for image upload
import sys








if __name__ == 'main':
    app.run(host='0.0.0.0', port=80)
