from shelfy import app

import flask
import os
from werkzeug.utils import secure_filename
import shelfy
import shelfy.functions


views = flask.Blueprint('views', __name__)

def allowed_file(file_name):
    return True


def get_submissions_files():

    path = shelfy.SHELFY_BASE_PATH + '/static/uploads'

    files = os.listdir(path)
    return files



@views.route('/uploads/<filename>', methods=['GET'])
def result(filename):

    # Get file names in submissions folder
    stored_filenames = get_submissions_files()


    for stored_filename in stored_filenames:
        print(stored_filename)
        if filename in stored_filename:
            matching_file = stored_filename

    # Calculate result
    functions.FullProcessImage(matching_file)



    return flask.render_template('submission.html', image_file = '/static/uploads/' + matching_file)


@views.route('/', methods=['GET', 'POST'])
def index():

    # Get method type
    method = flask.request.method



    if method == 'GET':
        print('get')
        return flask.render_template('index.html')



    if method == 'POST':
        print('wtf')
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            print('flask.request.files', flask.request.files)
            #flash('No file part')
            return flask.redirect(flask.request.url)



        file = flask.request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        print('file name', file.filename)
        if file.filename == '':
            print('no file')
            #flask.Flask.flash('No selected file')
            return flask.redirect(request.url)
        if file and allowed_file(file.filename):

            file.save('./uploads/' + secure_filename(file.filename))
            return flask.redirect('/uploads/' + file.filename.split('.')[0])
