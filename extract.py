import requests
from bs4 import BeautifulSoup

import transform


def get_pages_number(url: str) -> int:
    """from a url, retrieves the number of result pages to browse
    Args:
     url (str): a string with url
    Returns:
     nb_pages (int): one integer, -1 if not found
    """
    try:
        page = requests.get(url, timeout=5)

        if page.status_code == 200:
            page_parsed = BeautifulSoup(page.content, 'lxml')

            nb_pages = page_parsed.find('ul', {'class': 'pager'}).find('li', {'class': 'current'}).contents[0]
            nb_pages = transform.str_to_int(nb_pages.split()[-1])

        page.close()

    # exception quand le numero de page n'existe pas (càd qu'il n'y a qu'une page)
    # ex: http://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html
    except AttributeError:
        nb_pages = 1
    except TimeoutError as err:
        print("timeout lors de la récupération de la page", err)
    except Exception as err:
        print("Erreur lors de la récupération de la page", err)

    return nb_pages


def get_categories_url(url: str):
    """from the url of the main page, find the list of category urls
    Args:
     url: a string with url
    Returns:
     category_url_list: a list of url of categories
    """
    try:
        page = requests.get(url, timeout=5)

        if page.status_code == 200:

            page_parsed = BeautifulSoup(page.content, 'lxml')
            category_url_list = []

            for link in page_parsed.find('ul', {'class': 'nav nav-list'}).find_all_next('li'):

                # filtrage complémentaire
                if link.parent.attrs.get('class') is None:
                    category_url_list.append('http://books.toscrape.com/' + link.contents[1].attrs['href'])
        page.close()

    except TimeoutError as err:
        print("timeout lors de la récupération des pages de catégorie", err)
    except Exception as err:
        print("erreur lors de la récupération des pages de catégorie", err)

    return category_url_list


def categories_url_all_pages_list(category_url_list):
    """from a list of category urls, go through the entire list of category urls (if several result pages)
    Args:
     category_url_list: a urls list of first pages of category
    Returns:
     all_pages_list: the full list of category urls
    """
    all_pages_list = []

    for category_url in category_url_list:

        number_of_pages = get_pages_number(category_url)

        if number_of_pages == 1:
            # pas de modif, on reprend l'url tel quel
            all_pages_list.append(category_url)
        elif number_of_pages > 1:
            i = 1
            while i <= number_of_pages:
                # on récupère l'url de chaque page de résultat
                all_pages_list.append(category_url.replace('index.html', 'page-{}.html'.format(i)))
                i += 1

    return all_pages_list


def parsing_book_list_by_category(url_category):
    """from a category url, find all the books url and keep the category information in return
    Args:
     url_category: one url page of a category
    Returns:
     book_url_list: a list of books_dict {'category','book_url'}
    """
    book_url_list = []
    book_url_dict = {
        'category',
        'book_url'
    }

    try:
        page = requests.get(url_category, timeout=5)
        category = url_category.split('/')[-2]

        if page.status_code == 200:
            page_parsed = BeautifulSoup(page.content, 'lxml')

            # recherche des urls vers les livres
            for link in page_parsed.find('h3').find_all_next('a'):
                # condition complémentaire pour supprimer les doublons et le dernier lien (bouton next)
                if len(link.attrs) == 2:
                    book_url_dict = {'category': category, 'book_url': link.attrs['href'].replace('../../../', 'http://books.toscrape.com/catalogue/')}
                    book_url_list.append(book_url_dict)

        page.close()
    except TimeoutError as err:
        print("timeout lors de la récupération des pages de catégorie", err)
    except Exception as err:
        print("Erreur lors de la récupération des pages de catégorie", err)

    return book_url_list


def parsing_page_book(book_url_dict):
    """parsing a book page from one url and return a dict
    Args:
     book_url_dict:
        {
        'category': category of the book
        'book_url': url of the book
        }
    Returns:
     book_dict: a dict with informations about the book
        {
            'product_page_url': url of the book page
            'upc': upc unique code
            'title': title of the book
            'price_including_tax': price with taxes in pound sterling
            'price_excluding_tax': price without taxes in pound sterling
            'number_available': number of books availables
            'product_description': all informations about the book (summary,...)
            'category': category of book
            'review_rating': number of stars of the review rating
            'image_url': url of the image cover
        }
    """
    try:
        page = requests.get(book_url_dict.get('book_url'), timeout=5)
    except TimeoutError as err:
        print("timeout lors de la récupération des pages de catégorie", err)
    except Exception as err:
        print("Erreur lors de la récupération des pages de catégorie", err)

    if page.status_code == 200:

        page_parsed = BeautifulSoup(page.content, 'lxml')

        book_title = page_parsed.find('div', {'class': 'col-sm-6 product_main'}).find('h1').contents[0]

        try:
            # on va chercher l'element (sibling) suivant
            product_description = page_parsed.find('div', {'id': 'product_description'}).find_next_sibling().contents[0]
        # exception quand Product Description n'existe pas
        # ex: http://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html
        except AttributeError:
            product_description = ''

        # récupération du nombre indiqué dans le nom de la classe qui indique le nombre d'étoiles par ex : 'star-rating Two'
        review_rating = page_parsed.find('p', {'class': 'star-rating'}).attrs['class'][1]

        # url de l'image de couverture
        image_url = page_parsed.find('div', {'id': 'product_gallery'}).find('img').attrs.get('src').replace(r"../../", "http://books.toscrape.com/")

        # récupération des valeurs contenues dans le tableau "Product Information"
        product_info_list = [p.get_text() for p in page_parsed.find('table', {'class': 'table table-striped'}).findAll('td')]

        # Enregistrement dans un dictionnaire les éléments de chaque page
        book_dict = {
            'product_page_url': book_url_dict.get('book_url'),
            'upc': product_info_list[0],
            'title': book_title,
            'price_including_tax': transform.price_str_to_float(product_info_list[3]),
            'price_excluding_tax': transform.price_str_to_float(product_info_list[2]),
            'number_available': transform.str_to_int(product_info_list[5]),
            'product_description': product_description,
            'category': book_url_dict.get('category'),
            'review_rating': transform.book_nb_stars_to_decimal(review_rating),
            'image_url': image_url,
        }
    page.close()

    return book_dict


def parsing_books(url):
    """from the website url, retrieve all the information on the books on sale
    Args:
     url: main url page from the website
    Returns:
     book_dict: a dict with informations about ALL the books
        {
            'product_page_url': url of the book page
            'upc': upc unique code
            'title': title of the book
            'price_including_tax': price with taxes in pound sterling
            'price_excluding_tax': price without taxes in pound sterling
            'number_available': number of books availables
            'product_description': all informations about the book (summary,...)
            'category': category of book
            'review_rating': number of stars of the review rating
            'image_url': url of the image cover
        }
    """
    # on récupère la liste des URL des categories présentes sur la page d'accueil
    category_url_list = get_categories_url(url)

    # depuis la premiere page des catégories on teste et récupère l'ensemble des pages de chaque catégorie (page 2,...)
    category_url_list_all = categories_url_all_pages_list(category_url_list)

    books_url_list_all_pages = []
    # on récupère finalement l'ensemble des url des livres
    for category_url in category_url_list_all:
        books_url_list_all_pages.extend(parsing_book_list_by_category(category_url))

    books_list = []
    # parcours de chaque page de livre pour récupérer l'ensemble des informations souhaitées
    for book_url_dict in books_url_list_all_pages:
        books_list.append(parsing_page_book(book_url_dict))

    return books_list
