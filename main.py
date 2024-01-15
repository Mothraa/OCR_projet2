import requests
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re # gestion des expressions régulières (bibliothèque standard)
import datetime
import os.path




# informations à récupérer
# ● product_page_url
# ● universal_ product_code (upc)
# ● title
# ● price_including_tax
# ● price_excluding_tax
# ● number_available
# ● product_description
# ● category
# ● review_rating
# ● image_url


# mapping des chiffres écrits en toute lettre en valeurs décimales
def book_nb_etoile_en_decimal(arg):
    mapping_etoile = {
        'Zero':0,
        'One':1,
        'Two':2,
        'Tree':3,
        'Four':4,
        'Five':5
        }
    return mapping_etoile.get(arg, -1) # -1 si inexistant

def book_stock(arg):
        # print(re.findall("\d+", arg))
        if re.findall(r"\d+", arg)[0].isdigit():
            stock_nombre = int(re.findall(r"\d+", arg)[0])
        else:
            stock_nombre = -1
        
        return stock_nombre
    
# fonction qui récupère les informations de la page d'un livre a partir d'une url et renvoi un dictionnaire
def parsing_page_book(url_book):

    page = requests.get(url_book)

    if page.status_code == 200:
        #TODO ajouter une exception
        # "Parsage" d'une page de livre
        page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

        book_title = page_parsed.find('div',{'class':'col-sm-6 product_main'}).find('h1').contents[0]

        product_description = page_parsed.find('div',{'id':'product_description'}).find_next_sibling().contents # on va chercher l'element (sibling) suivant

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


# main
url = "http://books.toscrape.com/catalogue/the-girl-on-the-train_844/index.html"
print(parsing_page_book(url))

