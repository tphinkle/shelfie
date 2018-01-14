# Python standard library
import io
import requests

# Scraping
from bs4 import BeautifulSoup

# Scipy
import numpy as np
import matplotlib.pyplot as plt

# Scrapy
import scrapy.book


def FullPipeline(filepath):
    '''
    Given a filepath, performs the full processing pipeline,
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
    words = [Word.FromGoogleText(text) for text in texts[1:]]

    # Group the words into spines
    spines = GetSpinesFromWords(words)

    # Run the scraping pipeline for each spine
    books = []

    for spine in spines:

        # Get query
        search_query = spine.sentence

        # Process query
        book_info = GetBookInfo(search_query)

        # Create and store the new book object
        book = Book(book_info, spine)
        books.append(book)


    # Finally, return
    return books






def GetGoogleSearchURLFromQuery(search_query):
    '''
    Formats a string to be in the proper url for a google search
    '''

    return 'https://www.google.com/search?q='+search_query.replace(' ', '+').replace('-','')

def GetBookInfo(search_query):
    '''
    Grabs the Amazon link for a given search query and then scrapes the Amazon link for the book title
    '''
    search_url = GetGoogleSearchURLFromQuery(search_query)
    link = GetAmazonURLFromGoogleSearch(search_url)
    title = GetInfoFromAmazon(link)
    return title


def GetAmazonURLFromGoogleSearch(search_url):
    '''
    Two-part functions;
    first, uses `requests' module to perform the google search at search_url
    and grabs the HTML.
    Next, scrapes the resulting HTML for all links to amazon pages,
    and returns the list of amazon links
    '''

    # Perform the search and get the HTML
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    response = requests.get(url, headers=ua)
    content = response.content

    # Parse HTML content for amazon link; return first amazon url
    soup = BeautifulSoup(content, 'html.parser')
    amazon_urls = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if 'amazon' in str(url):
            amazon_urls.append(url)

    return amazon_urls



def GetInfoFromAmazon(url):
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
    book_info['title'] = GetTitleFromAmazonSoup(soup)

    # Authors
    book_info['authors'] = GetAuthorsFromAmazonSoup(soup)

    # Edition
    book_info['edition'] = GetEditionFromAmazonSoup(soup)

    # ISBN-10
    book_info['isbn-10'] = GetISBN10FromAmazonSoup(soup)

    # ISBN-13
    book_info['isbn-13'] = GetISBN13FromAmazonSoup(soup)

    return book_info



def GetTitleFromAmazonSoup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    title
    '''



    # Title
    # (ebook)

    ebook_children = soup.find_all(id = 'ebooksProductTitle')
    book_children = soup.find_all(id = 'productTitle')

    if ebook_children != []:
        title = soup.find_all(id = 'ebooksProductTitle')[0].contents[0]
    elif book_children != []:
        title = soup.find_all(id = 'productTitle')[0].contents[0]

    return title


def GetAuthorsFromAmazonSoup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    authors
    '''



    '''
    # Author
    author = soup.find_all(class_ = 'a-link-normal contributorNameID')[0].contents[0]
    '''


    return ''


def GetEditionFromAmazonSoup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    edition
    '''


    return ''


def GetISBN10FromAmazonSoup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    isbn-10 number
    '''


    '''
    # ISBN-10
    isbn_10 = soup.find_all(class_ = 'a-size-base a-color-base')[1].contents
    '''



    return ''


def GetISBN13FromAmazonSoup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    isbn-13 number
    '''


    '''
    # ISBN-13
    isbn_13 = soup.find_all(class_ = 'a-size-base a-color-base')[0].contents
    '''


    return ''
