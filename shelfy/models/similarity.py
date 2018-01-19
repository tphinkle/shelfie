# Imports
import Levenshtein

import numpy as np

MIN_SIMILARITY = 0
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
    book_info = book.book_info
    tokens = [word.string for word in book.spine.words]

    # Preprocess the variables
    book_info = preprocess_book_info(book_info)
    tokens = preprocess_book_tokens(tokens)

    # Calculate similarity score
    #similarity = single_token_levenshtein(tokens, info)
    similarity = single_token_inverse_weighted_levenshtein_tfidf(tokens, book_info)

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



def single_token_inverse_weighted_levenshtein_tfidf(tokens, book_words):
    '''
    Does a one-sided, weighted levenshtein score calculation, scaled by the
    TF-IDF value of the word in the data set
    inverse: The score goes like 1 over the weighted levenshtein 1/(1+L)
    'one-sided': Only matches from tokens->book words are considered, i.e. if
    a word shows up in book_words but not in tokens, there is no penalty
    'weighted': Divide the computed levenshtein distance by the maximal number
    of insertions and deletions that would be required under the worst case scenario,
    i.e. no letters overlap between the two words at all
    'levenshtein': Number of insertions and deletions needed to transform one
    word to another
    'tfidf': 'Term frequency inverse document frequency', scale the computed
    similarity score by the inverse of the number of times it appears across all
    book titles. To illustrate why this is important, considering the following two
    scenarios where in both cases only one word is detected along the book's spine:
        a) The word is 'dragon'; there are tons of books with the word 'dragon'
        in the title, so it's not very meaningful and therefore we shouldn't have
        much confidence in the match
        b) The word is 'elantris'; while still only a single word match, the word
        is basically present in the list of all available books only once, and
        therefore suggests a strong match
    '''

    total_similarity = 0



    # Loop over all tokens (words found on spine)
    for i, token in enumerate(tokens):
        temp_similarities = []

        # Loop over all book words (words associated with the book's info, e.g.
        # actual titles, publishers, etc.)
        L_token = len(token)
        for j, book_word in enumerate(book_words):
            L_book_word = len(book_word)

            distance = Levenshtein.distance(token, book_word)
            scale_factor = 2.*np.min([L_token, L_book_word])+np.abs(L_token-L_book_word)

            temp_similarities.append(1./(1+distance/scale_factor))

        try:
            max_similarity = np.max(temp_similarities)
        except:
            max_similarity =  MIN_SIMILARITY


        total_similarity += max_similarity

    return total_similarity




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
