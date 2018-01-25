# Python standard library
import datetime
import io
import os
import pickle
import sys
import time

# Scientific computing
import cv2

# Google cloud vision
from google.cloud import vision
from google.cloud.vision import types

# Shelfy
sys.path.append('..')
import main
import book_functions
import image_processing
import scraper
import similarity




def full_pipeline(img_path):
    '''
    Given a path to an img (img_path), performs the full processing pipeline,
    from loading the image to returning all Book objects found in the image
    Steps:
        1. Load the image
        2. Submit image to Google Cloud Vision api
        3. Create Spine objects in image
        4. Submit google queries for each Spine object
        5. Get the book info from Amazon for each Spine object
        6. Return the Books from each determined book info
    '''



    # Instantiates a google vision API client
    client = vision.ImageAnnotatorClient()

    # Loads the image into memory
    with io.open(img_path, 'rb') as img_file:
        content = img_file.read()
    img_bin = types.Image(content=content)



    # Query the image on google cloud vision API
    response = client.document_text_detection(image=img_bin)
    texts = response.text_annotations

    # Create word objects from the google word objects
    words = [book_functions.Word.from_google_text(text) for text in texts[1:]]
    
    # Get lines
    raw_img = cv2.imread(img_path)
    shelf_lines = image_processing.get_book_shelf_lines(raw_img, debug = False)
    spine_lines = image_processing.get_book_lines(raw_img, debug = False)

    # Group the words into spines (using lines)
    spines = book_functions.get_spines_from_words_lines(words, lines)

    # Run the scraping pipeline for each spine
    books = []

    for spine in spines:


        book_info = {}

        # Get query
        search_query = spine.sentence

        # Get google search url from query
        search_url = scraper.get_google_search_url_from_query(search_query)

        # Get first amazon link from google search url
        amazon_url = scraper.get_amazon_url_from_google_search(search_url)

        # Get isbn10 from amazon_url
        if amazon_url != None:
            isbn10 = scraper.get_isbn10_from_amazon_url(amazon_url, debug = True)



        else:
            # Couldn't get isbn10 from amazon link (or there was no amazon link)
            isbn10 = None



        # Time
        last_amazon_query = time.time()
        last_google_query = time.time()
        last_goodreads_query = time.time()


        # Create amazon bottlenose object
        amazon = scraper.get_amazon_object()

        # Run through all the APIs
        book_info = {}

        # Query apis for the isbn10
        if scraper.is_isbn10(isbn10, debug = True):


            # Try to get info from amazon products api
            if book_info == {}:
                book_info, book_price = scraper.query_amazon_products_api(isbn10, amazon)
                book_info['api'] = 'amazon products'


            '''
            # Try to get info from amazon
            if book_info == {}:
                dt = last_amazon_query - time.time()
                time.sleep(1-dt)
                book_info = scraper.query_amazon_page(isbn10, debug = True)
                last_amazon_query = time.time()

                book_info['api'] = 'amazon'


            # Try to get info from google API
            if book_info == {}:
                dt = last_google_query - time.time()
                time.sleep(1-dt)
                book_info = scraper.query_google_books_api(isbn10, debug = True)
                last_google_query = time.time()

                book_info['api'] = 'google'


            # Try to get info from good reads API
            if book_info == {}:
                dt = last_goodreads_query - time.time()
                time.sleep(1-dt)
                book_info = scraper.query_goodreads_api(isbn10, debug = True)
                last_goodreads_query = time.time()

                book_info['api'] = 'goodreads'

            '''



        # Create and store the new book object
        book = book_functions.Book(book_info, spine)

        book.set_price(book_price)



        # Flag book
        book.similarity = similarity.calculate_book_score(book)
        if book.similarity < 2:
            book.flag = False
        else:
            book.flag = True


        books.append(book)




    #utility.save_books()

    # Finally, return


    return books



def unpickle_all_books():
    '''
    Loads all of the books in the submissions files as a list called books
    '''



    submissions_base_path = main.SHELFY_BASE_PATH + '/static/submissions/'

    submissions = [dir for dir in os.listdir(submissions_base_path)]

    books_paths = [submissions_base_path + submission + '/books/' for submission in submissions]


    books = []
    for i in range(len(books_paths)):

        for file_path in os.listdir(books_paths[i]):
            with open(books_paths[i] + file_path, 'rb') as file_handle:
                books.append(pickle.load(file_handle))


    return books
