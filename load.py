import csv
from datetime import datetime
import os
import shutil

import requests


def create_directory(directory_path):
    """from a path name, create a directory
    Args:
     directory_path: path name
    Returns:
     None
    """
    os.makedirs(directory_path, exist_ok=True)

    return None


def same_category_book_list(category_name, list_of_books):
    """from a list of books, extract books with the same category
    Args:
     category_name: category name to filter
     list_of_books: list of all books
    Returns:
     books_list_by_category: a list of books of one category
    """
    books_list_by_category = []

    for book in list_of_books:
        if book['category'] == category_name:
            books_list_by_category.append(book)

    return books_list_by_category


def create_csv_file(csv_file_name, csv_directory, book_list):
    """create a csv file
    Args:
     csv_file_name: csv file name
     csv_directory: directory path
     book_list: list of books to save in csv file
    Returns:
     None
    """
    try:
        with open(csv_directory + csv_file_name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=book_list[0].keys(), delimiter=";")
            # on créé les entêtes de colonne
            writer.writeheader()
            # puis on écrit l'ensemble des lignes
            writer.writerows(book_list)

    except Exception as err:
        print("Un problème est survenu lors de l'écriture du csv :", err)

    return None


def write_images(directory, list_of_books):
    """from a list of books, extract images from their url to one directory
    Args:
    directory: directory to save file
    list_of_books: list of books to save the image for
    """
    for book in list_of_books:
        image_url = book['image_url']
        file_name = book['upc'] + '.jpg'

        try:
            r = requests.get(image_url, stream=True, timeout=5)
            if r.status_code == 200:

                # création du fichier
                with open(directory + file_name, 'wb') as file:
                    shutil.copyfileobj(r.raw, file)

                # on supprime la connexion
                del r
        except TimeoutError as err:
            print("timeout lors de la récupération de l'image", err)
        except Exception as err:
            print("erreur lors de la récupération et de l'enregistrement d'une image", err)

    return None


def write_files(list_of_books):
    """from a list of books, create a folder by category, a csv file
    and download covers in a subfolder images
    Args:
     list_of_books: list of books
    Returns:
     None
    """
    # date du jour pour le nommage des csv
    jour = datetime.now().strftime(r'%Y%m%d')

    for book in list_of_books:

        category_name = book['category']
        directory_csv = r".//output//" + category_name + r"//"

        # si le répertoire de la catégorie n'existe pas
        if os.path.exists(directory_csv) is False:

            # on créé l'arborescence
            create_directory(directory_csv)
            directory_images = directory_csv + r'images//'
            create_directory(directory_images)

            # on récupère l'ensemble des livres de la même catégorie
            list_of_books_by_category = same_category_book_list(category_name, list_of_books)

            # écriture du csv
            name_file_csv = str(jour + "-" + category_name + "-list.csv")
            create_csv_file(name_file_csv, directory_csv, list_of_books_by_category)

            # enregistrement des fichiers image
            write_images(directory_images, list_of_books_by_category)

    return None
