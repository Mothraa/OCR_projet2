import requests
from bs4 import BeautifulSoup

import transform


def parsing_category(url):
    """from the url of the main page, find the list of category urls
     Attrs:
    - url: a string with url
     Returns:
    - category_url_list: a list of url of categories
    """
    page = requests.get(url)

    if page.status_code == 200:
        # TODO ajouter une exception ?
        # lxml => interprétant "parser"
        page_parsed = BeautifulSoup(page.content, 'lxml')
        category_url_list = []

        for link in page_parsed.find('ul', {'class': 'nav nav-list'}).find_all_next('li'):

            # filtrage complémentaire
            if link.parent.attrs.get('class') is None:
                category_url_list.append('http://books.toscrape.com/' + link.contents[1].attrs['href'])

    return category_url_list


def category_url_all_pages_list(category_url_list):
    """from a list of category urls, go through the entire list of category urls (if several result pages)
     Attrs:
    - category_url_list: a urls list of first pages of category
     Returns:
    - all_pages_list: the full list of category urls
    """
    all_pages_list = []

    for category_url in category_url_list:

        i = 1
        while True:

            category_url_page = category_url

            # when there is only one page, we read index.html
            # then page-2.html, page-3.html...
            if i > 1:
                category_url_page = category_url.replace('index.html', 'page-{}.html'.format(i))

            # on regarde si il une page 2 existe
            test_page_existante = requests.get(category_url_page)

            # on sort de la boucle while si la page n'existe pas
            if test_page_existante.status_code == 200:

                all_pages_list.append(category_url_page)
                i += 1

            elif test_page_existante.status_code == 404:
                break
            else:
                print("Erreur d'accès à la page : ", test_page_existante.status_code)
                break

    return all_pages_list


def parsing_book_list_by_category(url_category):
    """from a category url, find all the books url
     Attrs:
    - url_category: one category page url
     Returns:
    - book_url_list: a list of book (url)
    """
    book_url_list = []

    book_url_dict = {
        'category',
        'book_url'
    }

    page = requests.get(url_category)
    category = url_category.split('/')[-2]

    if page.status_code == 200:
        page_parsed = BeautifulSoup(page.content, 'lxml')

        # recherche des urls vers les livres
        for link in page_parsed.find('h3').find_all_next('a'):
            # filtrage complémentaire pour supprimer les doublons et le dernier lien (bouton next)
            if len(link.attrs) == 2:
                book_url_dict = {'category': category, 'book_url': link.attrs['href'].replace('../../../', 'http://books.toscrape.com/catalogue/')}
                book_url_list.append(book_url_dict)

    return book_url_list


# fonction qui récupère les informations de la page d'un livre a partir d'une url et renvoi un dictionnaire
def parsing_page_book(category_name, url_book):

    page = requests.get(url_book)

    if page.status_code == 200:
        # TODO ajouter une exception ?
        # "Parsage" d'une page de livre
        # lxml => interprétant "parser"
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

        image_url = page_parsed.find('div', {'id': 'product_gallery'}).find('img').attrs.get('src').replace(r"../../", "http://books.toscrape.com/")

        # récupération des valeurs contenues dans le tableau "Product Information"
        liste_temp = [p.get_text() for p in page_parsed.find('table', {'class': 'table table-striped'}).findAll('td')]

    # création d'un dictionnaire pour stocker les éléments de chaque page
        book_dict = {
            'product_page_url': url_book,
            'upc': liste_temp[0],
            'title': book_title,
            'price_including_tax': liste_temp[3],
            'price_excluding_tax': liste_temp[2],
            'number_avaible': transform.stock_to_int(liste_temp[5]),
            'product_description': product_description,
            'category': category_name,
            'review_rating': transform.book_nb_etoile_en_decimal(review_rating),
            'image_url': image_url,
        }
    return book_dict
