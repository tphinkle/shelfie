# Python standard library
import csv
import io
import requests
import time

# Scraping
from bs4 import BeautifulSoup
import json
import bottlenose


# Hash
import hmac
import hashlib
import base64

# Program specific
import shelfy











google_books_api_key = 'AIzaSyBueagspvDe8R-prJ3bmqtEnr7fPTH10Xo'
goodreads_api_key = 'ooiawV83knPQnQ8If3eiSg'






def get_page_soup(url):
    '''
    Submits a request and returns the soup of the object;
    if 404, returns False
    '''

    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}

    response = requests.get(url, headers=ua)
    soup = BeautifulSoup(response.content, 'lxml')

    print('made it through get_page_soup!!!!!!!')

    return soup


def get_google_search_url_from_query(search_query):
    '''
    Formats a string to be in the proper url for a google search
    '''
    url = 'https://www.google.com/search?q=amazon+book+'+search_query.replace(' ', '+')
    return url

def is_isbn10(isbn10, debug = True):

    is_isbn = False



    # isbn10 must be a string
    if type(isbn10) == str:

        # isbn10 must be numeric and have length 10
        #print('is digit', isbn10.isdigit())
        #print('length', len(isbn10))
        is_isbn = ((len(isbn10) == 10))

    if debug:
        if is_isbn:
            print('isbn', isbn10, 'is isbn10')

        else:
            print('isbn', isbn10, 'is not isbn10')

    return is_isbn





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
    #'https://www.goodreads.com/book/show.xml?key=ooiawV83knPQnQ8If3eiSg&isbn=' + isbn
    rest_url = 'https://www.goodreads.com/book/show.xml?key=ooiawV83knPQnQ8If3eiSg&isbn=' + isbn10
    response = requests.get(rest_url, headers=ua)
    soup = BeautifulSoup(response.content, 'lxml')


    try:
        goodreads_id = soup.find('id').contents[0]
    except:
        pass
        if debug:
            print('Could not find goodreads id')
            return book_info


    # Query for book info
    rest_url = 'https://www.goodreads.com/book/show.xml?key=ooiawV83knPQnQ8If3eiSg&id='+goodreads_id
    response = requests.get(rest_url, headers=ua)

    soup = BeautifulSoup(response.content, 'lxml')

    # Title
    try:

        # Try to query 'original_title'
        original_title = soup.original_title.contents
        if len(original_title) > 0:
            original_title = original_title[0]

        # Try to query 'title'
        title = soup.title.contents
        if len(title) > 0:
            title = title[0]


        if original_title == []:
            actual_title = title
        else:
            actual_title = original_title

        if actual_title == []:
            actual_title = 'NONE'


        book_info['title'] = actual_title



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
    book_info['isbn10'] = isbn10

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


def query_amazon_page(isbn10, debug = False):
    '''
    Search amazon for an isbn10, and scrape the result
    '''

    # Create query
    query = isbn10

    # Get google search url
    google_search_url = get_google_search_url_from_query(query)

    amazon_url = get_amazon_url_from_google_search(google_search_url)


    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}


    response = requests.get(amazon_url, headers=ua)



    content = response.content

    soup = BeautifulSoup(content, 'html.parser')


    book_info = {}
    book_info['isbn10'] = isbn10


    # Get title
    try:
        book_info['title'] = get_title_from_amazon_soup(soup)

    except:
        pass
        if debug:
            print('Could not find book title (amazon)')

    # Get authors
    try:
        book_info['authors'] = get_authors_from_amazon_soup(soup)

    except:
        pass
        if debug:
            print('Could not find book authors (amazon)')

    # Get publisher
    try:
        book_info['publisher'] = get_publisher_from_amazon_soup(soup)


    except:
        pass
        if debug:
            print('Could not find book publisher (amazon)')



    # Get isbn10
    try:
        book_info['isbn10'] = get_isbn10_from_amazon_soup(soup)

    except:
        pass
        if debug:
            print('Could not find book isbn10 (amazon)')


    # Get isbn-13
    try:
        book_info['isbn13'] = get_isbn13_from_amazon_soup(soup)
    except:
        pass
        if debug:
            print('Could not find book isbn13 (amazon)')


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


def get_isbn10_from_google_search(search_url):
    '''
    Combines the two functions get_amazon_url_from_google_search() and
    get_isbn10_from_amazon_url
    '''

    amazon_url = get_amazon_url_from_google_search(search_url)
    isbn10 = get_isbn10_from_amazon_url(amazon_url)

    return isbn10


def get_amazon_url_from_google_search(search_url):
    '''
    Two-part functions;
    first, uses `requests' module to perform the google search at search_url
    and grabs the HTML.
    Next, scrapes the resulting HTML for all links to amazon pages,
    and returns the list of amazon links
    Returns None if no link can be found
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


        # Found an amazon url
        if ('www.amazon.com' in url) and ('/dp/' in url):

            amazon_url = url

            return amazon_url

    return None

def get_isbn10_from_amazon_url(url, debug = False):
    '''
    Given a url to an amazon page, gets the isbn10 number from that link.
    The isbn10 is the last 10 digits of the url that follow the forward slash
    '''
    isbn10 = url.split('/')[-1]
    if debug:
        print('found an isbn', isbn10)
    return url.split('/')[-1]



'''

def get_info_from_amazon(url):

    Given a url to an amazon page, will scrape that page for as much information
    as possible about the book; returns the information in `dict' format.



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

'''

def get_title_from_amazon_soup(soup):
    '''
    Scrapes soup created from an amazon page for the book's
    title
    '''



    # Title
    # (ebook)

    title = 'NONE'


    try:

        title = soup.find_all(id = 'productTitle')[0].contents[0]


        #ebook_children = soup.find_all(id = 'ebooksProductTitle')

        #if ebook_children != []:
            #title = soup.find_all(id = 'ebooksProductTitle')[0].contents[0]
        #elif book_children != []:
            #title = soup.find_all(id = 'productTitle')[0].contents[0]

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





'''
Amazon Products API
'''


def get_amazon_api_info():
    '''
    Opens a file to get amazon api info
    '''

    with open(shelfy.SHELFY_BASE_PATH + '/keys/amazon_product', 'r') as file_handle:
        reader = csv.reader(file_handle, delimiter = ',')

        aws_access_key_id = next(reader)[1]
        aws_secret_access_key = next(reader)[1]
        aws_associate_tag = next(reader)[1]

        return aws_access_key_id, aws_secret_access_key, aws_associate_tag


def get_amazon_object():
    '''
    Need to get an amazon object and pass it around to the
    functions that use the bottlenose module
    '''

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG = get_amazon_api_info()
    amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    return amazon


def query_amazon_products_api(isbn10, amazon, debug = False):
    '''
    Gets the book info using the amazon products api, given the isbn and a
    bottlenose.Amazon object (amazon)
    '''

    # Get response, turn into soup
    response = amazon.ItemLookup(ItemId=isbn10, ResponseGroup="ItemAttributes", SearchIndex="Books", IdType="ISBN").decode('utf-8')
    soup = BeautifulSoup(str(response), 'xml')


    # Get the book info
    book_info = {}
    book_info['isbn10'] = isbn10
    book_info['title'] = 'NONE'
    book_info['authors'] = 'NONE'
    book_info['publisher'] = 'NONE'


    # Price info
    price_info = None



    try:
        book_info['title'] = str(soup.ItemLookupResponse.Items.Item.ItemAttributes.Title.contents[0])
    except:
        pass
        if debug:
            print('could not find title (amazon products)')

    try:
        book_info['authors'] = str(soup.ItemLookupResponse.Items.Item.ItemAttributes.Author.contents[0])
    except:
        pass
        if debug:
            print('could not find author (amazon products)')

    try:
        book_info['publisher'] = str(soup.ItemLookupResponse.Items.Item.ItemAttributes.Publisher.contents[0])
    except:
        pass
        if debug:
            print('could not find publisher (amazon products)')

    try:
        price_info = get_prices_from_amazon_products(isbn10, amazon)
    except:
        pass
        if debug:
            print('could not find price info! (amazon products)')




    return book_info, price_info

class AmazonPrice(object):
    categories = ['Great', 'Fair', 'Poor']

    def __init__(self, prices, shipping_prices, qualities):

        # Get raw data
        self.prices = prices
        self.shipping_prices = shipping_prices
        self.qualities = qualities

        # Calculate means
        #self.price_mean = np.mean(self.prices)
        #self.shipping_prices_mean = np.mean(self.shipping_prices)




def get_prices_from_sales_page_soup(soup):
    '''
    Gets all of the pricing information from the soup
    '''

    prices = []
    shipping_prices = []
    qualities = []

    #print(soup.find_all(class_='a-section a-padding-small').find_all(class_='a-row a-spacing-mini olpOffer'))

    for offer in soup.find(class_='a-section a-padding-small').find_all(class_='a-row a-spacing-mini olpOffer'):

        print('asdf')

        # Get the pricing information
        try:
            price = offer.find(class_ = 'a-size-large a-color-price olpOfferPrice a-text-bold').contents[0].replace(' ','').replace('$','').replace(',','')
        except:
            price = 0
            print('could not find price...')
        try:
            shipping_price = offer.find(class_ = 'olpShippingPrice').contents[0].replace('$','').replace(',','')
        except:
            shipping_price = 0

        try:
            quality = offer.find(class_ = 'a-size-medium olpCondition a-text-bold').contents[0].replace(' ','').replace('\n','').replace('Used','').replace('-','')
        except:
            quality = 'NONE'
            print('could not find quality')


        print(price, shipping_price, quality)

        # Append to lists
        if price != 0:
            prices.append(float(price))
            shipping_prices.append(float(shipping_price))
            qualities.append(quality)

    print('made it through get_prices_from_sales_page!!!')

    return prices, shipping_prices, qualities



def get_prices_from_amazon_products(isbn, amazon):
    '''
    Returns a AmazonPrice object, an object that stores the pricing information for a book
    '''


    response = amazon.ItemLookup(ItemId=str(isbn), ResponseGroup="Offers",
    SearchIndex="Books", IdType="ISBN")

    soup = BeautifulSoup(response, 'lxml')

    price = soup.lowestnewprice.amount.contents[0]

    return price





    '''
    # Scraping...
    # Get the first sales page
    sales_url = get_first_sales_url_from_amazon(isbn, amazon)
    base_url = sales_url.split('?')[0]

    print('first sales url:', sales_url)
    print('base url:', base_url)

    # Loop over all sales page
    total_prices, total_shipping_prices, total_qualities = [],[],[]
    while sales_url != None:
        time.sleep(0.5)
        # Get the soup
        sales_page_soup = get_page_soup(sales_url)

        print(sales_page_soup)

        # Get the pricing information
        prices, shipping_prices, qualities = get_prices_from_sales_page_soup(sales_page_soup)

        print(prices, shipping_prices, qualities)

        # Append to total lists
        total_prices += prices
        total_shipping_prices += shipping_prices
        total_qualities += qualities

        # Get next sales url
        #sales_url = get_next_sales_url_from_sales_page_soup(sales_page_soup, base_url)
        sales_url = None


    book_price = AmazonPrice(total_prices, total_shipping_prices, total_qualities)


    return book_price
    '''






def get_first_sales_url_from_amazon(isbn, amazon):
    '''
    Gets the first sales page url from amazon for the given isbn
    '''

    response = amazon.ItemLookup(ItemId=isbn, ResponseGroup="Small",
    SearchIndex="Books", IdType="ISBN").decode('utf-8')
    soup = BeautifulSoup(str(response), 'xml')

    item_links = soup.Items.Item.ItemLinks.find_all('ItemLink')

    for item_link in item_links:
        description = item_link.Description.text

        if description == 'All Offers':
            return item_link.URL.text

def get_next_sales_url_from_sales_page_soup(soup, base_url):
    '''
    Given a url to a sales page, returns the next available sales page
    if it exists, otherwise returns None
    '''

    try:
        # There is a next button; get the url for it
        next_url = soup.find(class_='a-last').a['href']
    except:
        # Failed because no next link to follow; return None!
        return None

    # Append all the stuff before
    next_url = base_url + next_url


    print('made it through get_next_sales_url_from_amazon!!!!!!!!')

    return next_url
