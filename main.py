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


#a partir d'une url de category, retourne une liste des urls des livres
def parsing_category_book_list(url_category):
    
    page = requests.get(url_category)
    
    if page.status_code == 200:
        page_parsed = BeautifulSoup(page.content,'lxml')

        book_list = []

        # recherche des urls vers les livres
        for link in page_parsed.find('h3').find_all_next('a'):
            if len(link.attrs) == 2: # bidouille après analyse au debugger pour filtrer les doublons et le dernier lien (bouton next)
                book_list.append(link.attrs['href'].replace('../../../','http://books.toscrape.com/catalogue/'))


    return book_list           


def book_stock(arg):
        # print(re.findall("\d+", arg))
        if re.findall(r"\d+", arg)[0].isdigit():
            stock_nb_stars = int(re.findall(r"\d+", arg)[0])
        else:
            stock_nb_stars = -1
        
        return stock_nb_stars
    
# fonction qui récupère les informations de la page d'un livre a partir d'une url et renvoi un dictionnaire
def parsing_page_book(url_book):

    page = requests.get(url_book)

    if page.status_code == 200:
        #TODO ajouter une exception
        # "Parsage" d'une page de livre
        page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

        book_title = page_parsed.find('div',{'class':'col-sm-6 product_main'}).find('h1').contents[0]

        product_description = page_parsed.find('div',{'id':'product_description'}).find_next_sibling().contents[0] # on va chercher l'element (sibling) suivant

        review_rating = page_parsed.find('p',{'class':'star-rating'}).attrs['class'][1] # récupération du nombre indiqué dans le nom de la classe qui indique le nombre d'étoiles par ex : 'star-rating Two'
        #TODO faire un mapping des valeurs (map ??) pour modifier le texte "Two" en integer

        image_url = page_parsed.find('div',{'id':'product_gallery'}).find('img').attrs.get('src')#find('div',{'class':'item active'})

        # récupération des valeurs contenues dans le tableau "Product Information"
        liste_temp = [p.get_text() for p in page_parsed.find('table',{'class':'table table-striped'}).findAll('td')]

    # création d'un dictionnaire pour stocker les éléments de chaque page
        book_dict = {
                    'product_page_url':url,
                    'upc':liste_temp[0],
                    'title':book_title,
                    'price_including_tax':liste_temp[3],
                    'price_excluding_tax':liste_temp[2],
                    'number_avaible':book_stock(liste_temp[5]), # a décomposer par split de la chaine ou traitement en expression régulière
                    'product_description':product_description,
                    'category':liste_temp[1], # category == Product Type
                    'review_rating':book_nb_etoile_en_decimal(review_rating),
                    'image_url':image_url,
                    }
    return book_dict


##### main #####



url = "http://books.toscrape.com/catalogue/the-girl-on-the-train_844/index.html"
url_category = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/page-1.html"



# date du jour
jour = datetime.now().strftime(r'%Y%m%d') #'%Y-%m-%d %H:%M:%S'

# nommage du répertoire et du fichier de sortie
repertoire_ouput = r".//output//"
nom_fichier = str(repertoire_ouput + jour + "-book_list.csv")

# création du répertoire output si inexistant
os.makedirs(repertoire_ouput, exist_ok=True)


category_book_list = parsing_category_book_list(url_category)
print(category_book_list)

# ecriture du fichier csv
try:
    with open(nom_fichier, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=parsing_page_book(url).keys(), delimiter=";")
        writer.writeheader()
        writer.writerow(parsing_page_book(url)) #a remplacer par writerows quand le dictionnaire aura plus d'une ligne
except Exception as err:
    print("Un problème est survenu lors de l'écriture du csv :", err)