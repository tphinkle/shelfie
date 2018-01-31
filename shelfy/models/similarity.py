# Imports
import Levenshtein
import numpy as np

import sql_handle




MIN_SIMILARITY = 0
MAX_SIMILARITY = np.inf

def get_idf(word):
    '''
    Calculates the IDF score of the word as the sum of the counts in the
    'works', 'editions', 'authors', and 'publishers' tables
    '''


    # Set the command
    command = ''' SELECT count FROM {} WHERE words='{}'; '''


    # Get the total counts of the word across works, editions, authors, publishers
    total_counts = 0
    for table_name in ['works_counts', 'editions_counts', 'authors_counts', 'publishers_counts']:
        temp_command = command.format(table_name, word)
        result = sql_handle.SQLHandle.execute_postgresql_select(command.format(table_name, word))

        # Could not find result
        if result == None:
            counts = 0

        # Found counts
        else:
            counts = result[0][0]

        total_counts += counts


    # Get the idf


    # Normal case
    if total_counts > 0:
        idf = 1./total_counts

    else:
        idf = 1.




    return idf



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
    book_info = book.format_raw_book_info_to_words_list()
    tokens = book.format_raw_spine_words_to_words_list()

    # Preprocess the variables
    book_info = preprocess_words(book_info)
    tokens = preprocess_words(tokens)

    # Calculate similarity score
    #similarity = single_token_levenshtein(tokens, info)
    similarity = single_token_inverse_weighted_levenshtein_idf(tokens, book_info)

    return similarity


def preprocess_words(words):
    '''
    Preprocesses the book words that have been created by the
    get_book_words_from_book_info() function
    Possible steps:
        - Remove all non-alphanumeric characters
        - Lowercase all letters
    '''


    processed_words = words

    # Lower case
    processed_words = [word.lower() for word in processed_words]

    # Strip non-alphanumeric
    processed_words = [''.join(ch for ch in word if (ch.isalnum() or (ch == ' '))) for word in processed_words]


    # Remove non-strings
    processed_words = [word for word in processed_words if word != '']


    return processed_words



def edit_distance(word_1, word_2):
    L_1 = len(word_1)
    L_2 = len(word_2)

    distance = Levenshtein.distance(word_1, word_2)
    scale_factor = np.max([L_1, L_2])

    return distance/scale_factor

def single_token_inverse_weighted_levenshtein_idf(tokens, book_words):
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

    total_similarity = 1

    MIN_SIMILARITY = 0
    MAX_SIMILARITY = 100000


    # Loop over all tokens (words found on spine)
    for i, token in enumerate(tokens):
        temp_similarities = []

        # Loop over all book words (words associated with the book's info, e.g.
        # actual titles, publishers, etc.)
        L_token = len(token)
        for j, book_word in enumerate(book_words):
            temp_similarity = edit_distance(token, book_word)
            temp_similarities.append(temp_similarity)



        # Get the similarity
        edit_similarity = np.min(temp_similarities)



        # Get the idf of the word
        best_word = book_words[np.argmin(np.array(temp_similarities))]
        #idf = np.log(1.-get_idf(best_word))
        idf = get_idf(best_word)




        # Get final similarity
        if edit_similarity < .5:
            #similarity = edit_similarity*1./(-np.log(idf))
            similarity = (1./idf)/(138209219.)
        else:
            #similarity = 0
            similarity = 1


        #print(token, best_word, edit_similarity, similarity)


        # Get the inverse document frequency of the token
        total_similarity *= similarity



    return np.log(total_similarity)


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
