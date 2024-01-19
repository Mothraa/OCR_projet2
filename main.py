import requests
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re # gestion des expressions régulières (bibliothèque standard)
import csv
import shutil # pour la manipulation et l'enregistrement des fichiers (bibliothèque standard)
from datetime import datetime
import os


# mapping des chiffres écrits en toute lettre en valeurs décimales
def book_nb_etoile_en_decimal(arg):
    mapping_stars = {
        'Zero':0,
        'One':1,
        'Two':2,
        'Tree':3,
        'Four':4,
        'Five':5
        }
    return mapping_stars.get(arg, -1) # -1 si inexistant

# a partir de la page d'accueil retourne la liste des urls des catégories
def parsing_category(url):

    page = requests.get(url)

    if page.status_code == 200:
    #TODO ajouter une exception ?
        page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

        category_url_list = []

        for link in page_parsed.find('ul',{'class':'nav nav-list'}).find_all_next('li'):

            if link.parent.attrs.get('class') is None: # filtrage complémentaire
                category_url_list.append('http://books.toscrape.com/'+ link.contents[1].attrs['href'])

    return category_url_list

# a partir d'une liste d'url de categories on retourne la liste de toutes les pages des categories
def category_url_all_pages_list(category_url_list):

    all_pages_list = []

    for category_url in category_url_list:

        i = 1 # itérateur de la boucle
        while True:

            category_url_page = category_url

            if i> 1: # dans le cas ou il n'y a qu'une seule page, on lit index.html ; puis on va lire page-2.html, page-3.html...
                category_url_page = category_url.replace('index.html','page-{}.html'.format(i))

            test_page_existante = requests.get(category_url_page) # on regarde si il une page 2 existe

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



# a partir d'une url de category, retourne une liste des urls des livres
def parsing_book_list_by_category(url_category):
    #TODO ajouter le split de la category a partir de l'url, renvoyer un dict
    book_url_list = []

    book_url_dict = {
                    'category',
                    'book_url'
                    }
    
    page = requests.get(url_category)
    category = url_category.split('/')[-2]

    if page.status_code == 200:
        page_parsed = BeautifulSoup(page.content,'lxml')

        # recherche des urls vers les livres
        for link in page_parsed.find('h3').find_all_next('a'):
            if len(link.attrs) == 2: # filtrage complémentaire pour supprimer les doublons et le dernier lien (bouton next)
                book_url_dict = {'category' : category, 'book_url': link.attrs['href'].replace('../../../','http://books.toscrape.com/catalogue/')}
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
        #TODO ajouter une exception ?
        # "Parsage" d'une page de livre
        page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

        book_title = page_parsed.find('div',{'class':'col-sm-6 product_main'}).find('h1').contents[0]
#TODO : ajouter une exception quand Product Description n'existe pas. ex: http://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html
        product_description = page_parsed.find('div',{'id':'product_description'}).find_next_sibling().contents[0] # on va chercher l'element (sibling) suivant

        review_rating = page_parsed.find('p',{'class':'star-rating'}).attrs['class'][1] # récupération du nombre indiqué dans le nom de la classe qui indique le nombre d'étoiles par ex : 'star-rating Two'

        image_url = page_parsed.find('div',{'id':'product_gallery'}).find('img').attrs.get('src').replace(r"../../","http://books.toscrape.com/")

        # récupération des valeurs contenues dans le tableau "Product Information"
        liste_temp = [p.get_text() for p in page_parsed.find('table',{'class':'table table-striped'}).findAll('td')]

    # création d'un dictionnaire pour stocker les éléments de chaque page
        book_dict = {
                    'product_page_url':url_book,
                    'upc':liste_temp[0],
                    'title':book_title,
                    'price_including_tax':liste_temp[3],
                    'price_excluding_tax':liste_temp[2],
                    'number_avaible':stock_to_int(liste_temp[5]),
                    'product_description':product_description,
                    'category':category_name,
                    'review_rating':book_nb_etoile_en_decimal(review_rating),
                    'image_url':image_url,
                    }
    return book_dict


def write_image(repertoire, name, image_url):

    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(repertoire + name, 'wb') as file:
            shutil.copyfileobj(r.raw, file)
        del r
    return
     

# ecriture des fichiers csv et jpeg
def write_files(list_of_books_by_category):
    
    # date du jour
    jour = datetime.now().strftime(r'%Y%m%d') #'%Y-%m-%d %H:%M:%S'

    # init de la boucle while de lecture de la liste de livres
    i = 0
    category_name = list_of_books_by_category[i]['category'] # catégorie de la ligne courante
    previous_category_name ='' # catégorie de la ligne précédente


    while i < len(list_of_books_by_category):

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

                writer = csv.DictWriter(f, fieldnames=list_of_books_by_category[i].keys(), delimiter = ";")

                # lors de la première itération sur le fichier on créé les entêtes de colonne
                if category_name != previous_category_name and i < len(list_of_books_by_category):
                    writer.writeheader()
                #TODO a extraire proprement de la boucle if car doublon de code. On pourrait ne laisser que previous_category_name = category_name mais code pas clair a comprendre
                    writer.writerow(list_of_books_by_category[i])
                    # enregistrement du fichier image
                    link_image = list_of_books_by_category[i]['image_url']
                    name_image = list_of_books_by_category[i]['upc'] + '.jpg'
                    write_image(repertoire_images, name_image, link_image)

                    i += 1
                    previous_category_name = category_name
                    category_name = list_of_books_by_category[i]['category']
                ####### fin TODO #####

                while category_name == previous_category_name and i < len(list_of_books_by_category):
                    writer.writerow(list_of_books_by_category[i])
                    # enregistrement du fichier image
                    link_image = list_of_books_by_category[i]['image_url']
                    name_image = list_of_books_by_category[i]['upc'] + '.jpg'
                    write_image(repertoire_images, name_image, link_image)

                    i += 1
                    previous_category_name = category_name
                    category_name = list_of_books_by_category[i]['category']

        except Exception as err:
            print("Un problème est survenu lors de l'écriture du csv :", err)
        continue






##### main #####

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