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
goodreads_api_key = 'ooiawV83knPQnQ8If3eiSg'

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

        # Get google search url from query
        search_url = get_google_search_url_from_query(search_query)

        # Get first amazon link from google search url
        amazon_url = get_amazon_url_from_google_search(search_url)

        # Get isbn10 from amazon_url
        isbn10 = get_isbn10_from_amazon_url(amazon_url)


        # Query apis for the isbn10
        if is_isbn10(isbn10):


            # Try to get info from google API
            book_info = query_google_books_api(isbn10)

            # Else try to get info from good reads API
            if book_info == {}:
                book_info = query_goodreads_api(isbn10)


            # Create and store the new book object
            book = book_functions.Book(book_info, spine)


        # Couldn't find an isbn10, just append a book w/ no info
        else:
            book = book_functions.Book({}, spine)



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


def query_goodreads_api(isbn10, debug = False):
    '''
    Gets book information from goodreads API call
    '''

    # Main info

    book_info = {}
    book_info['isbn10'] = isbn10





    # Header
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}

    # Query for goodreads ID
    rest_url = 'https://www.goodreads.com/search/index.xml?key=ooiawV83knPQnQ8If3eiSg&q=' + isbn10
    response = requests.get(rest_url, headers=ua)
    soup = BeautifulSoup(response.content, 'lxml')

    goodreads_id = print(soup.find('id').contents[0])

    # Query for book info
    rest_url = 'https://www.goodreads.com/book/show.xml?key=ooiawV83knPQnQ8If3eiSg&id='+goodreads_id
    response = requests.get(rest_url, headers=ua)

    soup = BeautifulSoup(response.content, 'lxml')

    # Title
    try:
        book_info['title'] = soup.original_title.contents[0]
    except:
        pass
        if debug:
            print('Could not find title for isbn 10', isbn10, '(goodreads api)')

    # Authors
    try:
        book_info['authors'] = [child.find('name').contents[0] for child in soup.authors.children if child.find('name') != -1]
    except:
        pass
        if debug:
            print('Could not find authors for isbn 10', isbn10, '(goodreads api)')

    # Publisher
    try:
        book_info['publisher'] = soup.find('publisher').contents[0]
    except:
        pass
        if debug:
            print('Could not find publisher for isbn 10', isbn10, '(goodreads api)')


    return book_info

def query_google_books_api(isbn10, debug = False):
    '''
    Gets book info from google book API call    '''


    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}


    rest_url = 'https://www.googleapis.com/books/v1/volumes?key='+google_books_api_key+'&q=isbn:' + isbn10
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



    # Get isbn10
    try:
        book_info['isbn10'] = content['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']

    except:
        pass
        if debug:
            print('Could not find book isbn10')


    # Get isbn-13
    try:
        book_info['isbn13'] = content['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']

    except:
        pass
        if debug:
            print('Could not find book isbn13')


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
    Given a url to an amazon page, gets the isbn10 number from that link.
    The isbn10 is the last 10 digits of the url that follow the forward slash
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

    # isbn10
    book_info['isbn10'] = get_isbn10_from_amazon_soup(soup)

    # isbn10
    book_info['isbn10'] = get_isbn13_from_amazon_soup(soup)

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
    isbn10 number
    '''

    isbn10 = 'NONE'

    try:
        book_details = soup.findAll(id = 'detail-bullets')


        for line in str(book_details[0]).split('\n'):
            if 'isbn10' in line:
                isbn10 = line[20:30]
                break




    except:
        pass

    return isbn10




def get_isbn13_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    isbn10 number
    '''


    isbn10 = 'NONE'

    try:
        book_details = soup.findAll(id = 'detail-bullets')


        for line in str(book_details[0]).split('\n'):
            if 'isbn13' in line:
                isbn10 = line[20:34]
                break




    except:
        pass

    return isbn10
