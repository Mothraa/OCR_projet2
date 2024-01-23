import csv
from datetime import datetime
import os
import shutil

import requests


def create_directories(directory_path):

    if os.path.exists(directory_path) is False :
        # création du répertoire correspondant à la catégorie
        os.makedirs(directory_path, exist_ok=True)
        # création d'un sous répertoire images
        repertoire_images = directory_path + r'images//'
        os.makedirs(repertoire_images, exist_ok=True)

    return None


def create_csv_file(csv_file_name, list_of_books_by_category):
    try:
        with open(csv_file_name, 'w', encoding='utf-8', newline='') as f:

            writer = csv.DictWriter(f, fieldnames=list_of_books_by_category[0].keys(), delimiter=";")

            # lors de la première itération sur le fichier on créé les entêtes de colonne
            writer.writeheader()
            for book in list_of_books_by_category:
                writer.writerow(book)


                # enregistrement du fichier image
                link_image = book['image_url']
                name_image = book['upc'] + '.jpg'
#                write_image(link_image, repertoire_images, name_image)

    except Exception as err:
        print("Un problème est survenu lors de l'écriture du csv :", err)

    return None


def write_image(image_url, directory, file_name):
    """from an url, save the file in a local directory
     Attrs:
    - image_url : url of the image
    - repertoire: directory to save file
    - file_name : file name
    """
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(directory + file_name, 'wb') as file:
            shutil.copyfileobj(r.raw, file)
        del r
    return None


# ecriture des fichiers csv et jpeg
def write_files(list_of_books_by_category):
    # date du jour au format %Y-%m-%d %H:%M:%S'

    jour = datetime.now().strftime(r'%Y%m%d')
    category_name = list_of_books_by_category[i]['category']


    i = 0
    while i < len(list_of_books_by_category):

        repertoire_ouput = r".//output//" + category_name + r"//"
        nom_fichier_csv = str(repertoire_ouput + jour + "-" + category_name + "-list.csv")

        # si on change de catégorie, donc que le repertoire n'existe pas, on le créé
        create_directories(repertoire_ouput)
        create_csv_file(nom_fichier_csv, list_of_books_by_category)


