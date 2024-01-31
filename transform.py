import re


def book_nb_stars_to_decimal(arg: str) -> int:
    """Transform a string with a number write in letters to an integer
    Args:
     arg: a string
    Returns:
     stars_number: one integer, -1 if not found
    """
    mapping_stars = {
        'Zero': 0,
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    stars_number = mapping_stars.get(arg, -1)
    return stars_number


def stock_to_int(arg: str) -> int:
    """extract an integer from a string
    Args:
     arg: a string
    Returns:
     stock_nb: one integer, -1 if not found
    """
    if re.findall(r"\d+", arg)[0].isdigit():
        stock_nb = int(re.findall(r"\d+", arg)[0])
    else:
        stock_nb = -1
    return stock_nb


def price_str_to_float(arg: str) -> float:
    """remove the symbol £ (ASCII \xa3) from string and transform to float
    Args:
     arg: a string
    Returns:
     float
    """
    arg = re.sub(r'£', '', arg)
    return float(arg)
