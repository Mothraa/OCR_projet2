import extract
import load


url = "http://books.toscrape.com/"

# scrapping du site web pour récupérer les informations sur les livres
books_list = extract.parsing_books(url)

# ecriture des fichiers en sortie (csv et images)
load.write_files(books_list)
