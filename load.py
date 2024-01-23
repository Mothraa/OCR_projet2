import csv
from datetime import datetime
import os
import shutil

import requests


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
