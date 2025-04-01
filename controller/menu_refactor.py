import os, sys
# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import configparser, click, jwt, datetime
from datetime import datetime, timedelta
from argon2 import PasswordHasher

from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import NoResultFound


from models import User, Team, Event, Contract, Client
# from views.cli import display_login_registration_menu
from utils.token_utils import  create_netrc_file, get_netrc_path, get_tokens_from_netrc, \
    update_tokens_in_netrc, get_user_from_access_token
from utils.token_utils import generate_tokens, is_token_expired
from utils.db_utils import create_database_if_not_existent

# Récupérer les infos de connexion à la base de données depuis le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

db_user = config['database']['user']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['dbname']

# create_database_if_not_existent(db_user, db_password, db_host, db_name)

# Créer objet de connexion à la base de données
engine = create_engine(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
    echo=False
) # Ajouter echo=True pour afficher les logs des commandes SQL, retirer en production
conn = engine.connect()

# Afficher les tables de la base de données
"""result = conn.execute(text("SHOW TABLES;"))
for row in result:
    print(row)"""

Session = sessionmaker(bind=engine)
session = Session()

# Permet de mapper les classes avec les tables
Base = declarative_base()
# Créer les tables
Base.metadata.create_all(engine)

# Clé secrète pour signer le jeton JWT
SECRET_KEY = "nvlzhvgi476hcich90796"

@click.group()
def cli():
    pass


