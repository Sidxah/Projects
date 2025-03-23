# HotelFinder

HotelFinder est une application interactive permettant de rechercher, visualiser et gérer des hôtels en Île-de-France, avec des fonctionnalités avancées de cartographie et de gestion des favoris.

## Fonctionnalités

- Recherche d’hôtels proches d’une adresse saisie par l’utilisateur.
- Affichage des hôtels sur une carte interactive avec des marqueurs.
- Gestion des favoris avec ajout par double-clic dans une table affichant les détails des hôtels.
- Tri et filtrage des hôtels par prix, classement, et distance.
- Gestion et stockage des données via PostgreSQL.

## Technologies utilisées

- **Python 3** : Langage principal pour le développement.
- **PyQt5** : Interface utilisateur graphique.
- **Folium** : Cartographie interactive.
- **PostgreSQL** : Base de données relationnelle.
- **psycopg2** : Connexion Python à PostgreSQL.

## Prérequis

Assurez-vous d'avoir les outils et bibliothèques suivants installés sur votre machine :

- **Python 3.8+**
- **PostgreSQL** : Pour la base de données des hôtels.
- Bibliothèques Python :
  - PyQt5
  - Folium
  - psycopg2

Pour installer les bibliothèques Python, exécutez :
```bash
pip install PyQt5 folium psycopg2
