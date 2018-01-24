'''
INCLUDE THIS IF RUNNING VIA
flask run (or, through compile.sh)
'''

# Imports
import flask
import os
from werkzeug.utils import secure_filename    # Needed for image upload
import sys
import shelfy







if __name__ == 'main':
    shelfy.app.run(host='0.0.0.0', port=80)
