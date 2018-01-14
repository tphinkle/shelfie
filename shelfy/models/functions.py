import io

import numpy as np
import matplotlib.pyplot as plt

import requests
from bs4 import BeautifulSoup
import time

from google.cloud import vision
from google.cloud.vision import types










def GetGoogleSearchLinkFromQuery(search_query):
    '''
    Formats a string to be in the proper url for a google search
    '''

    return 'https://www.google.com/search?q='+search_query.replace(' ', '+').replace('-','')

def GetBookInfo(search_query):
    '''
    Grabs the Amazon link for a given search query and then scrapes the Amazon link for the book title
    '''

    link = GetAmazonLinkFromGoogleSearch(search_query)
    title = GetTitleFromAmazonLink(link)
    return title


def GetAmazonLinkFromGoogleSearch(search_query):

    # Perform google search
    link = GetGoogleSearchLink(search_query)

    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    print('link = ', link)
    response = requests.get(link, headers=ua)
    content = response.content

    # Parse for amazon link
    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        if 'amazon' in str(url):
            return url

def GetTitleFromAmazon(url):
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    response = requests.get(url, headers=ua)
    content = response.content

    # Parse for amazon link
    soup = BeautifulSoup(content, 'html.parser')



    # Title
    # (ebook)

    ebook_children = soup.find_all(id = 'ebooksProductTitle')
    book_children = soup.find_all(id = 'productTitle')

    if ebook_children != []:
        title = soup.find_all(id = 'ebooksProductTitle')[0].contents[0]
    elif book_children != []:
        title = soup.find_all(id = 'productTitle')[0].contents[0]



    '''
    # Author
    author = soup.find_all(class_ = 'a-link-normal contributorNameID')[0].contents[0]






    # ISBN-13
    isbn_13 = soup.find_all(class_ = 'a-size-base a-color-base')[0].contents






    # ISBN-10
    isbn_10 = soup.find_all(class_ = 'a-size-base a-color-base')[1].contents
    '''





    return title, author
