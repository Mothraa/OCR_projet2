import extract
import transform
import load


# main
url = "http://books.toscrape.com/"

# on récupère la liste des URL des categories présentes sur la page d'accueil
category_url_list = extract.get_categories_url(url)

# depuis la premiere page des catégories on teste et récupère l'ensemble des pages de catégories
category_url_list_all = extract.categories_url_all_pages_list(category_url_list)

books_url_list_all_pages = []
# on récupère finalement l'ensemble des url des livres

for category_url in category_url_list_all:
    books_url_list_all_pages.extend(extract.parsing_book_list_by_category(category_url))

books_list = []
# parcours de chaque page de livre pour récupérer l'ensemble des informations souhaitées
for book_url in books_url_list_all_pages:
    books_list.append(extract.parsing_page_book(book_url.get('category'), book_url.get('book_url')))


# ecriture des fichiers en sortie (csv et images)
load.write_files(books_list)
