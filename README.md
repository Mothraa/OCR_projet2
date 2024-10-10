# Script d'extraction des prix de books.toscrape.com

## À propos

Formation OpenClassRooms - Developpeur d'application python - Projet 2

initiation à Python et au webscraping, en utilisant comme ressources le site dédié : http://books.toscrape.com/


## Prérequis

Python >=3.12.1 et une connexion internet

## Installation

Cloner le repository
```bash
git clone https://github.com/Mothraa/OCR_projet2.git
```
Créer l'environnement avec [venv](https://docs.python.org/fr/3/library/venv.html)
```bash
python -m venv env
```
Activer l'environnement

- sous linux ou mac
```bash
source env/bin/activate
```
- sous windows
```bash
env/scripts/activate
```
Utiliser le gestionnaire de package [pip](https://docs.python.org/fr/dev/installing/index.html) pour installer les librairies python
```bash
pip install -r requirements.txt
```

## Utilisation

Executer le script main.py
dans le terminal :
```bash
python main.py
```

## Langages & Frameworks

Développé sous python 3.12.1
avec l'aide des librairies :
- BeautifulSoup4 https://pypi.org/project/beautifulsoup4/
- requests https://pypi.org/project/requests/

## Documentation

### Table des matières

  - [Extraction des données](#extract)
  - [Transformation des données](#transform)
  - [Chargement des données](#load)

### Extraction des données

A partir de la page d'accueil du site http://books.toscrape.com/ l'ensemble de chaque page de livre est parcouru (scraping) pour y récupérer les informations ci-dessous :

* *product_page_url* : lien url vers le livre
* *universal_product_code (upc)* : code universel et unique du livre
* *title* : titre de l'ouvrage
* *price_including_tax* : prix avec taxes, **en livres sterling**
* *price_excluding_tax* : prix sans taxes, **en livres sterling**
* *number_available* : quantités disponibles
* *product_description* : description du produit (résumé,...)
* *category* : catégorie de l'ouvrage (suivant l'arborescence du site books.toscrape.com)
* *review_rating* : notation du livre de 1 à 5 étoiles
* *image_url* : lien url vers l'image de couverture

### Transformation des données

4 attributs sont modifiés :
* *price_including_tax* : suppression du symbole £ (livres sterling)
* *price_excluding_tax* : suppression du symbole £ (livres sterling)
* *number_available* : extraction du nombre (entier) de la chaine de caractère
* *review_rating* : conversion du nombre d'étoiles en nombre (entier)

### Chargement des données

Pour chaque livre, ses informations sont sauvegardées au format tabulaire (csv) ainsi que leurs couvertures au format .jpg (jpeg)

#### CSV

Les exports CSV sont générés dans le répertoire \output du script avec un sous répertoire par catégorie.

Les fichiers CSV sont au format UTF-8 avec séparateur ";" (semicolon) et comme nommage : **[export_date]-[category_name]-list.csv**

Les colonnes ci-dessous sont créées dans l'ordre :
    product_page_url
    upc
    title
    price_including_tax
    price_excluding_tax
    number_available
    product_description
    category
    review_rating
    image_url

Une ligne du CSV représente un livre de la catégorie.

#### Images

Les images (couvertures des livres) sont stockées dans le sous répertoire \images de chaque catégorie.
Chaque image est nommée suivant son identifiant UPC (universal product code) unique, indiqué dans le fichier CSV.

#### Arborescence

On obtient l'arborescence ci-dessous :
```bash
\output\[category_name]\[export_date]-[category_name]-list.csv
                       \images\[id_upc].jpg
                               ...
```
Exemple :
```bash
\output\mystery_3\20240125-mystery_3-list.csv
                 \images\0c7b9cf2b7662b65.jpg
```

## Gestion des versions

La dénomination des versions suit la spécification décrite par la [Gestion sémantique de version](https://semver.org/lang/fr/)

Les versions disponibles ainsi que les journaux décrivant les changements apportés sont disponibles depuis [la section releases](https://github.com/Mothraa/OCR_projet2/releases)

## Licence

Voir le fichier [LICENSE](./LICENSE.md) du dépôt.
