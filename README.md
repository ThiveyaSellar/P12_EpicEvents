# P12_EpicEvents

## About this project

EpicEvents, an event consulting and management company, needs a Custom Relationship Management software to improve the organization of customer events.

## Installation

- Clone remote repository :

```
https://github.com/ThiveyaSellar/P12_EpicEvents.git
```

- Create a virtual environment in the project :
```
python -m venv env
```

- Activate virtual environment :
- Linux :
```
source env/bin/activate
```
- Windows :
```
env\Scripts\activate.bat
```

- Install the necessary packages from requirements.txt :
```
pip install -r requirements.txt
```
- Installer MYSQL :
Télécharger le serveur et le client MySQL sur https://dev.mysql.com/downloads/mysql/
- Création d'un utilisateur pour la base de données :
- Fichier .sql y mettre les commandes de création de l'utilisateur et de création de la base de données

- CREATE DATABASE epic_events_db;
- 
- Configuration base de données :
Fichier config_empty.ini, remplir
- Fichier MYSQL avec les commandes
- Exécution alembic
- Création de la base de donnée à l'exécution du programme
- Création au préalable
- Ouvrir MySQL Shell
- Création de la base de données en se connectant à mysql shell et exécuté les commandes ou préparer un fichiier sql avec les commandes qu'ils exécuteront
- MYSQL Shell
```
mysqlsh
```
- Launch the CRM Software
```
python main.py
```

## Environnement virtuel OK
## Installation librairie OK
## Base de données mysql
## Flake 8 OK
## tests
## accès au dashboard ? guide installation ?
## Détailler les bibliothèques du projet ou les savoir expliquer
## Fichier .netrc windows que faire pour linux ?



# Flake8

Flake8 is a package for checking that code complies with PEP8 guidelines.
- Configuration file : .flake8
- Generate flake 8 report :
```
flake8 > flake-report.txt
```

qu'est-ce que j'ai fait dans les autres readme ?
et si je commencais avec j'avais et je complétais
est-ce u'il y a quelque part le développement que j'avais fait il était bien je trouve

si je l'ai fait une fois je peux e refaire
plutot me positionner dans la création que dans la récupération de quelque chose d'oubliée

qu'est-ce qui me parle plus ? le plus simple et je diminue la compléxité 
point de départ readme vide avec python main.py et activation environnemnt virtuel

soit fichier sql à exécuter ou bien 
excéuter les commandes alemebic ?

créer un répertoire sur le bureau
importer le projet essayer de l'installer
comment installer mysql

c'est ce que j'ai fait 
j'ai installé mysql
je me suis connecter en tant que root à @localhost à la base de donnée epic_events

préparer l'option ou la ersonne a mysql
fichier sql
exécution commande alemenibc
option pas mysql guide d'installation