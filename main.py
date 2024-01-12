import requests
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re #gestion des expressions régulières (bibliothèque standard)
import datetime
import os.path

page = requests.get("http://books.toscrape.com/catalogue/the-girl-on-the-train_844/index.html")

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

if page.status_code == 200:
    #TODO ajouter une exception

    # "Parsage" d'une page de livre
    page_parsed = BeautifulSoup(page.content,'lxml') # lxml => interprétant "parser"

    book_title = page_parsed.find('div',{'class':'col-sm-6 product_main'}).find('h1')

    # product_description = page_parsed.find('div',{'id':'product_description'}).next_sibling.next_sibling # on va chercher l'element (sibling) suivant 2 fois (la 1ere fois c'est un \n)
    product_description = page_parsed.find('div',{'id':'product_description'}).find_next_sibling() # on va chercher l'element (sibling) suivant

    # review_rating : class:'star-rating*' 
    review_rating = page_parsed.find('p',{'class':'star-rating'}).attrs['class'][1] # récupération du nombre indiqué dans le nom de la classe qui indique le nombre d'étoiles par ex : 'star-rating Two'
    #TODO faire un mapping des valeurs (map ??) pour modifier le texte "Two" en integer

    image_url = page_parsed.find('div',{'id':'product_gallery'}).find('img')#find('div',{'class':'item active'})

    print(image_url)


    # récupération des valeurs contenues dans le tableau "Product Information"
    liste_temp = [toto.get_text() for toto in page_parsed.find('table',{'class':'table table-striped'}).findAll('td')]

#création d'un dictionnaire pour stocker les éléments de chaque page
    book_dict = {
                #'product_page_url':,
                'upc':liste_temp[0],
                'title':book_title.get_text(),
                'price_including_tax':liste_temp[3],
                'price_excluding_tax':liste_temp[2],
                'number_avaible':liste_temp[5], # a décomposer par split de la chaine ou traitement en expression régulière
                'product_description':product_description,
                'category':liste_temp[1], #Product Type
                'review_rating':review_rating,
                'image_url':image_url,
                }
    # print(book_dict)

    # test regex
    # if re.findall("\d+", liste_temp[5])[0].isdigit():
    #     michel = int(re.findall("\d+", liste_temp[5])[0])
    #     print(michel)
    # else:



