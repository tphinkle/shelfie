from shelfy import app

import flask
import os
from werkzeug.utils import secure_filename


views = flask.Blueprint('views', __name__)

def allowed_file(file_name):
    return True


@views.route('/submissions/', methods=['GET'])
def


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
            return flask.redirect('/uploads/' + filename)


    '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
