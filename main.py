import extract
import transform
import load


# main
url = "http://books.toscrape.com/"

# on récupère la liste des categories
category_url_list = extract.parsing_category(url)

# depuis la premiere page des catégories on teste et récupère l'ensemble des pages de catégories
category_url_list_all = extract.category_url_all_pages_list(category_url_list)

j = 0
category_book_list_all_pages = []
# on récupère finalement l'ensemble des url des livres
while j < len(category_url_list_all):
    category_book_list_all_pages.extend(extract.parsing_book_list_by_category(category_url_list_all[j]))
    j += 1

j = 0
books_list = []
# parcours de chaque page de livre pour récupérer l'ensemble des informations souhaitées
while j < len(category_book_list_all_pages):
    books_list.append(extract.parsing_page_book(category_book_list_all_pages[j].get('category'), category_book_list_all_pages[j].get('book_url')))
    j += 1

# ecriture des fichiers en sortie (csv et images)
load.write_files(books_list)
