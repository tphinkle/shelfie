from shelfy import app

import flask
import os
from werkzeug.utils import secure_filename
import shelfy
from shelfy.models import book_functions, scraper, server


views = flask.Blueprint('views', __name__)




@views.route('/uploads/<submission_id>', methods=['GET'])
def uploads(submission_id):




    raw_img_file_path = server.get_raw_image_path_from_submission_id(submission_id)




    return flask.render_template('submission.html', image_file = raw_img_file_path)


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
        return flask.render_template('index.html')



    if method == 'POST':


        # No file found in the POST submission
        if 'file' not in flask.request.files:
            return flask.redirect(flask.request.url)



        # File was found
        file = flask.request.files['file']

        # No file name submitted
        if file.filename == '':
            return flask.redirect(request.url)

        # File was found, and is an allowable file type
        if file:

            # Create a new submission folder for the submission
            submission_id = server.create_new_submission(file)

            # Process the file and filename
            file_path = server.get_raw_image_path_from_submission_id(submission_id)



            # Process the image
            books = scraper.full_pipeline(file_path)


            # Pickle and save the books
            server.pickle_save_books(books, submission_id)

            # Save json of book info
            server.save_book_info(books, submission_id)


            # Save the annotated images








            return flask.redirect('/uploads/' + submission_id)
