# Python standard library
import io
import requests
import time

# Scraping
from bs4 import BeautifulSoup

# Scipy
import numpy as np
import matplotlib.pyplot as plt

# Google cloud vision
from google.cloud import vision
from google.cloud.vision import types


# Shelfy
from shelfy.models import book_functions


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

    # Group the words into spines
    spines = book_functions.get_spines_from_words(words)

    # Run the scraping pipeline for each spine
    books = []

    for spine in spines:

        # Get query
        search_query = spine.sentence

        # Process query
        book_info = get_book_info(search_query)

        # Create and store the new book object
        book = book_functions.Book(book_info, spine)



        if book.book_info['title'] != 'NONE':
            print('title', book.book_info['title'])
            print('tokens', [word.string for word in book.spine.words])

            

            books.append(book)


    # Finally, return
    return books






def get_google_search_url_from_query(search_query):
    '''
    Formats a string to be in the proper url for a google search
    '''

    return 'https://www.google.com/search?q='+search_query.replace(' ', '+').replace('-','')

def get_book_info(search_query):
    '''
    Grabs the Amazon link for a given search query and then scrapes the Amazon link for the book title
    '''


    search_url = get_google_search_url_from_query(search_query)



    t0 = time.time()
    amazon_url = get_amazon_url_from_google_search(search_url)
    t1 = time.time()
    #print('get google search', t1 - t0)



    if amazon_url != None:
        t0 = time.time()
        book_info = get_info_from_amazon(amazon_url)
        t1 = time.time()
        #print('get amazon', t1 - t0)
    else:
        book_info = {}



    return book_info


def is_google_search_redirect(url):
    if url[:7] == '/search':
        return True
    else:
        return False


def get_amazon_url_from_google_search(search_url):
    '''
    Two-part functions;
    first, uses `requests' module to perform the google search at search_url
    and grabs the HTML.
    Next, scrapes the resulting HTML for all links to amazon pages,
    and returns the list of amazon links
    '''

    # Perform the search and get the HTML
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    response = requests.get(search_url, headers=ua)
    content = response.content

    # Parse HTML content for amazon link; return first amazon url
    soup = BeautifulSoup(content, 'html.parser')
    amazon_urls = []
    for link in soup.find_all('a'):
        url = link.get('href')

        # Found an amazon link
        if 'amazon' in str(url):
            if is_google_search_redirect(url):
                url = get_amazon_url_from_google_search('https://www.google.com' + url)


            return url

    return None



def get_info_from_amazon(url):
    '''
    Given a url to an amazon page, will scrape that page for as much information
    as possible about the book; returns the information in `dict' format.
    '''


    # Get HTML for the amazon url
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    response = requests.get(url, headers=ua)
    content = response.content


    # Parse for amazon link
    soup = BeautifulSoup(content, 'html.parser')


    book_info = {}

    # Title
    book_info['title'] = get_title_from_amazon_soup(soup)

    # Authors
    book_info['authors'] = get_authors_from_amazon_soup(soup)

    # ISBN-10
    book_info['isbn-10'] = get_isbn10_from_amazon_soup(soup)

    # ISBN-13
    book_info['isbn-13'] = get_isbn13_from_amazon_soup(soup)

    return book_info



def get_title_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    title
    '''



    # Title
    # (ebook)

    title = 'NONE'

    try:
        ebook_children = soup.find_all(id = 'ebooksProductTitle')
        book_children = soup.find_all(id = 'productTitle')

        if ebook_children != []:
            title = soup.find_all(id = 'ebooksProductTitle')[0].contents[0]
        elif book_children != []:
            title = soup.find_all(id = 'productTitle')[0].contents[0]

    except:
        pass



    return title


def get_authors_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    authors
    '''

    author = 'NONE'

    try:
        author = soup.find_all(class_ = 'a-link-normal contributorNameID')[0].contents[0]
    except:
        pass



    return author



def get_isbn10_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    isbn-10 number
    '''

    isbn_10 = 'NONE'

    try:
        book_details = soup.findAll(id = 'detail-bullets')


        for line in str(book_details[0]).split('\n'):
            if 'ISBN-10' in line:
                isbn_10 = line[20:30]
                break




    except:
        pass

    return isbn_10




def get_isbn13_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    isbn-13 number
    '''


    isbn_13 = 'NONE'

    try:
        book_details = soup.findAll(id = 'detail-bullets')


        for line in str(book_details[0]).split('\n'):
            if 'ISBN-13' in line:
                isbn_13 = line[20:34]
                break




    except:
        pass

    return isbn_13
