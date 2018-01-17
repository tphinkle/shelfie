# Imports
import Levenshtein

import numpy as np


MAX_SIMILARITY = np.inf

def calculate_book_score(book):
    '''
    Calculates the 'similarity' of a book object, that is how close the tokens
    that were detected in the image align with the actual information available
    about the book
    Has three steps:
    1. Get the relevant variables out of the book data structure
    2. Preprocess the variables
    3. Calculate the similarity score
    '''

    # Get book variables
    info = book.book_info
    tokens = [word.string for word in book.spine.words]

    # Preprocess the variables
    info = preprocess_book_info(info)
    tokens = preprocess_book_tokens(tokens)

    # Calculate similarity score
    similarity = single_token_levenshtein(tokens, info)

    return similarity


def preprocess_book_info(book_info):
    '''
    Preprocesses the book words that have been created by the
    get_book_words_from_book_info() function
    Possible steps:
        - Remove all non-alphanumeric characters
        - Lowercase all letters
    '''

    title = book_info['title']
    authors = ''.join([author for author in book_info['authors']])
    publisher = book_info['publisher']

    if title == 'NONE':
        print('title none')
        title = ''

    if authors == 'NONE':
        authors = ''

    if publisher == 'NONE':
        publisher = ''


    book_words = title + ' ' + authors + ' ' + publisher


    # Lower case
    processed_book_words = book_words.lower()

    # Strip non-alphanumeric
    processed_book_words = ''.join(ch for ch in processed_book_words if (ch.isalnum() or (ch == ' ')))

    # Turn into list
    processed_book_words = processed_book_words.split(' ')

    # Remove non-strings
    processed_book_words = [word for word in processed_book_words if word != '']

    return processed_book_words

def preprocess_book_tokens(tokens):

    # Convert list to single string
    processed_tokens = ''.join([token + ' ' for token in tokens])

    # Lower case
    processed_tokens = processed_tokens.lower()

    # Strip non-alphanumeric
    processed_tokens = ''.join(ch for ch in processed_tokens if (ch.isalnum() or (ch == ' ')))

    # Turn into list
    processed_tokens = processed_tokens.split(' ')

    # Remove non-strings
    processed_tokens = [token for token in processed_tokens if token != '']

    return processed_tokens







def single_token_levenshtein(tokens, book_words):
    '''
    Does a one-sided, weighted levenshtein score calculation
    'one-sided': Only matches from tokens->book_words are considered, i.e.
    if a word shows up book_words but not in tokens, there is no penalty
    'weighted': Divide the computed levenshtein distance by the length of the
    token
    '''



    total_distance = 0



    # Loop over all tokens (words found on spine)
    for i, token in enumerate(tokens):
        temp_distances = []

        # Loop over all book words (words associated with the book's info, e.g.
        # actual titles, publishers, etc.)
        for j, book_word in enumerate(book_words):
            distance = Levenshtein.distance(token, book_word)
            temp_distances.append(distance)

        try:
            minimum_distance = np.min(temp_distances)/len(token)
        except:
            minimum_distance = MAX_SIMILARITY


        total_distance += minimum_distance

    return total_distance
