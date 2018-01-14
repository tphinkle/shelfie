# Python standard library
import io
import os

# Scipy
import numpy as np
import matplotlib.pyplot as plt

# Shelfy
import shelfy
import shelfy.book





def generate_unique_id_incremental():
    '''
    Generates a key for a submission
    Submissions are 9 digit numbers that incrementally increase
    '''

    # Get all folder names
    submissions_path = SHELFY_BASE_PATH + '/submissions'
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
    '''

    # Get a unique ID for the submission
    id = generate_unique_id_incremental()


    # Create the main and sub folders for the submission
    directory = shelfy.SHELFY_BASE_PATH + '/submissions' + '/' + id
    os.makedirs(directory)
    os.makedirs(directory + '/annotated_imgs')

    # Save the image to the newly created folder
    file_extension = file.name.split('.')[-1]
    file.save(directory + '/raw-img' + '.' + file_extension
