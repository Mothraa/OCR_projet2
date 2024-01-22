import re
import csv
import shutil
from datetime import datetime
import os

import requests
from bs4 import BeautifulSoup


def book_nb_etoile_en_decimal(arg):
    """Transforme une chaine de chiffres écrits en toute lettre en nombre par mapping de valeurs
     Attrs:
    - arg: une chaine
     Returns:
    - one integer, -1 if not found
    """
    mapping_stars = {
        'Zero': 0,
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return mapping_stars.get(arg, -1)


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


# extrait de la chaine de caractère du stock d'un livre, un nombre décimal
def stock_to_int(arg):
    if re.findall(r"\d+", arg)[0].isdigit():
        stock_nb = int(re.findall(r"\d+", arg)[0])
    else:
        stock_nb = -1
    return stock_nb


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
            'number_avaible': stock_to_int(liste_temp[5]),
            'product_description': product_description,
            'category': category_name,
            'review_rating': book_nb_etoile_en_decimal(review_rating),
            'image_url': image_url,
        }
    return book_dict


def write_image(repertoire, name, image_url):

    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(repertoire + name, 'wb') as file:
            shutil.copyfileobj(r.raw, file)
        del r
    return None


# ecriture des fichiers csv et jpeg
def write_files(list_of_books_by_category):
    # date du jour au format %Y-%m-%d %H:%M:%S'
    jour = datetime.now().strftime(r'%Y%m%d')

    # init de la boucle while de lecture de la liste de livres
    i = 0
    # catégorie de la ligne courante
    category_name = list_of_books_by_category[i]['category']
    # catégorie de la ligne précédente
    previous_category_name = ''

    while i < len(list_of_books_by_category):

        # TODO os.path.exists(chemin)
        # si on change de catégorie, on créé un nouveau répertoire et fichier csv
        if category_name != previous_category_name:
            # nommage du répertoire et du fichier de sortie
            repertoire_ouput = r".//output//" + category_name + r"//"
            nom_fichier_csv = str(repertoire_ouput + jour + "-" + category_name + "-list.csv")
            # création du répertoire output et du sous répertoire de la catégorie si inexistant
            os.makedirs(repertoire_ouput, exist_ok=True)
            # création du répertoire du sous répertoire images dans la catégorie
            repertoire_images = repertoire_ouput + r'images//'
            os.makedirs(repertoire_images, exist_ok=True)

        try:
            with open(nom_fichier_csv, 'w', encoding='utf-8', newline='') as f:

                writer = csv.DictWriter(f, fieldnames=list_of_books_by_category[i].keys(), delimiter=";")

                # lors de la première itération sur le fichier on créé les entêtes de colonne
                if category_name != previous_category_name:
                    writer.writeheader()
                # TODO a extraire proprement de la boucle if car doublon de code.
                # On pourrait ne laisser que previous_category_name = category_name
                # mais code pas clair a comprendre
                    writer.writerow(list_of_books_by_category[i])
                    # enregistrement du fichier image
                    link_image = list_of_books_by_category[i]['image_url']
                    name_image = list_of_books_by_category[i]['upc'] + '.jpg'
                    write_image(repertoire_images, name_image, link_image)

                    i += 1
                    # si on arrive en fin de liste de category
                    if i < len(list_of_books_by_category):
                        previous_category_name = category_name
                        category_name = list_of_books_by_category[i]['category']
                    else:
                        break
                # fin TODO

                while category_name == previous_category_name:
                    writer.writerow(list_of_books_by_category[i])
                    # enregistrement du fichier image
                    link_image = list_of_books_by_category[i]['image_url']
                    name_image = list_of_books_by_category[i]['upc'] + '.jpg'
                    write_image(repertoire_images, name_image, link_image)

                    i += 1
                    # si on arrive en fin de liste de category
                    if i < len(list_of_books_by_category):
                        previous_category_name = category_name
                        category_name = list_of_books_by_category[i]['category']
                    else:
                        break

        except Exception as err:
            print("Un problème est survenu lors de l'écriture du csv :", err)
        continue


# main
url = "http://books.toscrape.com/"

# on récupère la liste des categories
category_url_list = parsing_category(url)

# depuis la premiere page des catégories on teste et récupère l'ensemble des pages de catégories
category_url_list_all = category_url_all_pages_list(category_url_list)

j = 0
category_book_list_all_pages = []
# on récupère finalement l'ensemble des url des livres
while j < len(category_url_list_all):
    category_book_list_all_pages.extend(parsing_book_list_by_category(category_url_list_all[j]))
    j += 1

j = 0
books_list = []
# parcours de chaque page de livre pour récupérer l'ensemble des informations souhaitées
while j < len(category_book_list_all_pages):
    books_list.append(parsing_page_book(category_book_list_all_pages[j].get('category'), category_book_list_all_pages[j].get('book_url')))
    j += 1

# ecriture des fichiers en sortie (csv et images)
write_files(books_list)
