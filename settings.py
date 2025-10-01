import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class Settings:

    def __init__(self):
        # A la création de l'objet les attributs sont initialisés
        # Les méthodes sont appelées
        # Dans ces méthodes on initialise les attributs
        self.engine = None
        self.conn = None
        self.session = None
        self.sentry_dsn = None
        self.set_config()
        self.set_database_config()
        self.set_sentry_config()
        self.get_database_connection()
        self.create_session()
        self.create_tables()
        self.get_secret_key()

    def set_config(self):
        # Read configuration from config file
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def set_database_config(self):
        self.database_config = DatabaseConfig(self.config)

    def set_sentry_config(self):
        self.sentry_dsn = self.config['sentry']['SENTRY_DSN']

    def get_database_connection(self):
        # Connexion à la base de données qu'une seule fois
        if self.engine is None and self.conn is None:
            # Créer objet de connexion à la base de données
            # echo=True affiche logs commandes SQL, à retirer en production
            db_user = self.database_config.db_user
            db_password = self.database_config.db_password
            db_host = self.database_config.db_host
            db_name = self.database_config.db_name
            self.engine = create_engine(
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
                echo=False
            )
            self.conn = self.engine.connect()
        return self.conn

    def create_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_tables(self):
        # Permet de mapper les classes avec les tables
        Base = declarative_base()
        # Créer les tables
        Base.metadata.create_all(self.engine)

    def get_secret_key(self):
        self.secret_key = self.config['jwt']['SECRET_KEY']


class DatabaseConfig:

    def __init__(self, config):
        self.db_user = config['database']['user']
        self.db_password = config['database']['password']
        self.db_host = config['database']['host']
        self.db_name = config['database']['dbname']
