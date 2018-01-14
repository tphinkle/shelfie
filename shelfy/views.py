from shelfy import app

import flask
import os
from werkzeug.utils import secure_filename
import shelfy
from shelfy.functions import functions


views = flask.Blueprint('views', __name__)




@views.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):


    filepath = shelfy.SHELFY_BASE_PATH + '/static/uploads/' + filename


    # Create and save all annotated images

    # Get all books objects
    books = functions.FullProcessImage(shelfy.SHELFY_BASE_PATH + '/static/uploads/' + matching_file)



    return flask.render_template('submission.html', image_file = '/static/uploads/' + matching_file)


@views.route('/', methods=['GET', 'POST'])
def index():
    '''
    The index; a simple interface for allowing a user to submit an image
    to query
    methods:
        GET: The main page, has a 'submit image' button
        POST: After the submit/query/request button is hit, the file will be saved
        to the server and the user will be redirected to the uploads page
    '''

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

            # Create a new submission folder for the submission
            server.create_new_submission(file)
            return flask.redirect('/uploads/' + file.filename.split('.')[0])
