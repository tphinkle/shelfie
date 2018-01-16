# Python standard library
import io
import requests
import time

# Scraping
from bs4 import BeautifulSoup
import json

# Scipy
import numpy as np
import matplotlib.pyplot as plt

# Google cloud vision
from google.cloud import vision
from google.cloud.vision import types


# Shelfy
from shelfy.models import book_functions



google_books_api_key = 'AIzaSyBueagspvDe8R-prJ3bmqtEnr7fPTH10Xo'

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

        books.append(book)


    # Finally, return
    return books






def get_google_search_url_from_query(search_query):
    '''
    Formats a string to be in the proper url for a google search
    '''
    url = 'https://www.google.com/search?q=amazon+'+search_query.replace(' ', '+')
    print('google search query', url)
    return url

def is_isbn10(isbn10):
    return isbn10.isdigit() and (len(isbn10) == 10)

def get_book_info(search_query):
    '''
    Grabs the Amazon link for a given search query and then scrapes the Amazon link for the book title
    '''


    search_url = get_google_search_url_from_query(search_query)



    t0 = time.time()
    amazon_url = get_amazon_url_from_google_search(search_url)
    t1 = time.time()
    #print('get google search', t1 - t0)


    book_info = {}
    if amazon_url != None:

        isbn_10 = get_isbn10_from_amazon_url(amazon_url)

        if is_isbn10(isbn_10):
            book_info = query_google_books_api(isbn_10)





    return book_info


def query_google_books_api(isbn_10, debug = False):
    '''
    Gets google information
    '''


    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}


    rest_url = 'https://www.googleapis.com/books/v1/volumes?key='+google_books_api_key+'&q=isbn:' + isbn_10
    response = requests.get(rest_url, headers=ua)



    content = json.loads(response.content)


    book_info = {}

    # Get title
    try:
        book_info['title'] = content['items'][0]['volumeInfo']['title']
    except:
        pass
        if debug:
            print('Could not find book title')

    # Get authors
    try:
        book_info['authors'] = content['items'][0]['volumeInfo']['authors']

    except:
        pass
        if debug:
            print('Could not find book authors')

    # Get publisher

    try:
        book_info['publisher'] = content['items'][0]['volumeInfo']['publisher']

    except:
        pass
        if debug:
            print('Could not find book publisher')



    # Get isbn-10
    try:
        book_info['isbn_10'] = content['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']

    except:
        pass
        if debug:
            print('Could not find book isbn_10')


    # Get isbn-13
    try:
        book_info['isbn_13'] = content['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']

    except:
        pass
        if debug:
            print('Could not find book isbn_13')


    return book_info



def is_google_search_redirect(url):
    '''
    Determines whether a url on a google page is an internal redirect to another
    revised google search
    '''

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


        url = str(link.get('href'))


        # Found an amazon link
        if 'www.amazon.com' in url:

            print('found an amazon url', url)


            amazon_url = url

            return amazon_url

    return None

def get_isbn10_from_amazon_url(url):
    '''
    Given a url to an amazon page, gets the ISBN-10 number from that link.
    The isbn-10 is the last 10 digits of the url that follow the forward slash
    '''
    return url.split('/')[-1]



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

    # Publisher
    book_info['publisher'] = get_publisher_from_amazon_soup(soup)

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


def get_publisher_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    publisher
    '''

    publisher = 'NONE'

    try:
        book_details = soup.findAll(id = 'detail-bullets')


        for line in str(book_details[0]).split('\n'):
            if 'Publisher' in line:
                publisher = line.split(':')[-1].replace('</b>','').replace('</li>','')




    except:
        pass

    return publisher



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
