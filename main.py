import requests
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re # gestion des expressions régulières (bibliothèque standard)
import csv
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
    #TODO ajouter une exception
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


def book_stock(arg):
        # print(re.findall("\d+", arg))
        if re.findall(r"\d+", arg)[0].isdigit():
            stock_nb_stars = int(re.findall(r"\d+", arg)[0])
        else:
            stock_nb_stars = -1
        
        return stock_nb_stars
    
# fonction qui récupère les informations de la page d'un livre a partir d'une url et renvoi un dictionnaire
def parsing_page_book(category_name, url_book):

    page = requests.get(url_book)

    if page.status_code == 200:
        #TODO ajouter une exception
        # "Parsage" d'une page de livre
        page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

        book_title = page_parsed.find('div',{'class':'col-sm-6 product_main'}).find('h1').contents[0]

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
                    'number_avaible':book_stock(liste_temp[5]),
                    'product_description':product_description,
                    'category':category_name,
                    'review_rating':book_nb_etoile_en_decimal(review_rating),
                    'image_url':image_url,
                    }
    return book_dict

# ecriture du fichier csv
def write_csv(list_of_books_by_category):

    # date du jour
    jour = datetime.now().strftime(r'%Y%m%d') #'%Y-%m-%d %H:%M:%S'


    category_name = list_of_books_by_category[0]['category']


    # nommage du répertoire et du fichier de sortie
    repertoire_ouput = r".//output//" + category_name + r"//"
    nom_fichier = str(repertoire_ouput + jour + "-" + category_name + "_list.csv")

    # création du répertoire output si inexistant
    os.makedirs(repertoire_ouput, exist_ok=True)

    try:
        with open(nom_fichier, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list_of_books_by_category[0].keys(), delimiter = ";")#parsing_page_book(url).keys(), delimiter=";")
            writer.writeheader()
            writer.writerows(list_of_books_by_category) #a remplacer par writerows quand le dictionnaire aura plus d'une ligne
    except Exception as err:
        print("Un problème est survenu lors de l'écriture du csv :", err)
    return



##### main #####

url = "http://books.toscrape.com/"

# toto = [{1 : 1}, {1 : 9}, {1 : 5}, {1 : 2}, {1 : 5}, {9 : 1}, {1 : 1}, {5 : 8}]
# student_tuples = [
#     ('john', 'A', 15),
#     ('jane', 'B', 12),
#     ('dave', 'B', 10),
# ]
# toto_sorted = sorted(student_tuples, key=lambda student: student[2])

# print(toto)
# print(toto_sorted)
#conversion en tuples pour pouvoir trier
# d1 = {"x": 1, "y": 2, "z": 3}
# l1 = list(d1.items())
# print(l1)

category_url_list = parsing_category(url)


temp = category_url_all_pages_list(category_url_list)

j = 0
category_book_list_all_pages = []

while j < len(temp):
    category_book_list_all_pages.extend(parsing_book_list_by_category(temp[j]))
    j += 1
    if j == 2: #pour test, ne traite que les 2 premieres
        break

j = 0
list_of_books_by_category = []
while j < len(category_book_list_all_pages):
    #TODO modifier parsing_page_book pour ajouter en entrée la category
    list_of_books_by_category.append(parsing_page_book(category_book_list_all_pages[j].get('category'), category_book_list_all_pages[j].get('book_url')))
    j += 1
    if j == 2: #pour test, ne traite que les 2 premieres
        break


write_csv(list_of_books_by_category)