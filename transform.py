import re


def book_nb_etoile_en_decimal(arg):
    """Transforme une chaine de chiffres écrits en toute lettre en nombre par mapping de valeurs
     Attrs:
    - arg: une chaine
     Returns:
    - one integer, -1 if not found
    """
    mapping_stars = {
        'Zero': 0,
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return mapping_stars.get(arg, -1)


# extrait de la chaine de caractère du stock d'un livre, un nombre décimal
def stock_to_int(arg):
    if re.findall(r"\d+", arg)[0].isdigit():
        stock_nb = int(re.findall(r"\d+", arg)[0])
    else:
        stock_nb = -1
    return stock_nb
