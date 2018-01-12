from shelfy import app

import flask
import os
import io
from werkzeug.utils import secure_filename
import shelfy
from shelfy.functions import functions


views = flask.Blueprint('views', __name__)

def allowed_file(file_name):
    return True


def get_submissions_files():

    path = shelfy.SHELFY_BASE_PATH + '/static/uploads'

    files = os.listdir(path)
    return files



@views.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):

    # Get file names in submissions folder
    stored_filenames = get_submissions_files()


    for stored_filename in stored_filenames:
        print(stored_filename)
        if filename in stored_filename:
            matching_file = stored_filename

    print('shelfy functions:')
    print(dir(functions))

    # Calculate result
    img = functions.FullProcessImage(matching_file)



    return flask.render_template('submission.html', image_file = '/static/uploads/' + matching_file)


@views.route('/', methods=['GET', 'POST'])
def index():

    # Get method type
    method = flask.request.method



    if method == 'GET':
        print('get')
        return flask.render_template('index.html')



    if method == 'POST':


        # No file found in the POST submission
        if 'file' not in flask.request.files:
            return flask.redirect(flask.request.url)



        # File was found
        file = flask.request.files['file']

        # No file name submitted
        if file.filename == '':
            print('no file')
            return flask.redirect(request.url)

        # File was found, and is an allowable file type
        if file and allowed_file(file.filename):

            file.save(shelfy.SHELFY_BASE_PATH + '/static/uploads/' + secure_filename(file.filename))
            return flask.redirect('/uploads/' + file.filename.split('.')[0])
