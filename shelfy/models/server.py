# Python standard library
import io
import os
import pickle

# Scipy
import numpy as np
import matplotlib.pyplot as plt

# Shelfy
import shelfy
from shelfy.models import book

# Google cloud visionfrom google.cloud import vision
from google.cloud import vision
from google.cloud.vision import types





def generate_unique_id_incremental():
    '''
    Generates a key for a submission
    Submissions are 9 digit numbers that incrementally increase
    '''

    # Get all folder names
    submissions_path = shelfy.SHELFY_BASE_PATH + '/submissions'
    submission_ids = os.listdir(submissions_path)

    # If no submissions, initialize with first submission value
    if submission_ids == []:
        return '000000000'

    # Submissions exist; find the latest submission and increment
    submission_ids = [int(submission) for submission in submissions]
    submission_ids.sort()
    last_submission_id = submission_ids[-1]
    new_submission_id = str(last_submission_id + 1).zfill(9)

    return new_submission_id



def create_new_submission(file):
    '''
    Saves a new submission to the server;
    Generates the correct folder and subfolders for the submission,
    and saves the file to the folder.
    Returns the id of the new submission
    '''

    # Get a unique ID for the submission
    id = generate_unique_id_incremental()


    # Create the main and sub folders for the submission
    directory = shelfy.SHELFY_BASE_PATH + '/submissions/' + id
    os.makedirs(directory)
    os.makedirs('/raw_img')
    os.makedirs(directory + '/annotated_imgs')
    os.makedirs(directory + '/books')

    # Save the image to the newly created folder
    file_extension = file.name.split('.')[-1]
    file.save(directory + '/raw_img/raw_img' + '.' + file_extension)



    return id


def get_raw_image_path_from_submission_id(submission_id):
    '''
    Returns the full file path to the raw_img associated iwth submission_id
    '''

    # Get the directory of the raw_file file for the submission_id
    file_directory = shelfy.SHELFY_BASE_PATH + '/submissions/' + submission_id + '/raw_img'

    # get file path
    file_path = [file_name for file_name in os.listdir(file_directory) \
     if os.path.osfile(join(file_directory, file_name))][0]

    return file_path



def get_pickle_directory_from_submission_id(submission_id):
    '''
    Returns the correct path to the pickle directory for submission_id
    '''

    # Get the directory of the raw_file file for the submission_id
    file_directory = shelfy.SHELFY_BASE_PATH + '/submissions/' + submission_id + '/books'



def pickle_save_books(books, submission_id):
    '''
    Pickles book objects and saves them to the correct submission folder
    '''


    # Get the directory to which to save the book
    pickle_directory = get_pickle_directory_from_submission_id(submission_id)

    # Pickle and save the books to the correct directory
    for i, book in enumerate(books):
        with open(pickle_directory + '/' + str(i), 'wb') as file_handle:
            pickle.dump(book, file_handle)
