import configparser
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import jwt

# Fichier de configuration
config = configparser.ConfigParser()
config.read('config.ini')

db_user = config['database']['user']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['dbname']

# Créer objet de connexion à la base de données
# Indiquer le chemin de la base de donnée
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}", echo=True) # Retirer echo en production car log les commandes SQL
conn = engine.connect()
result = conn.execute(text("SHOW TABLES;"))
print(result)
# Afficher les résultats
for row in result:
    print(row)

Session = sessionmaker(bind=engine)
session = Session()

# Permet de mapper les classes avec les tables
Base = declarative_base()

# Définir la table utilisateur
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    password = Column(String(100))

    def __repr__(self):
        return f'User {self.name}'

# Créer les tables
Base.metadata.create_all(engine)

user = User(name='John Snow', password='johnspassword')
session.add(user)
session.commit()

print(user.id)  # None
query = session.query(User).filter_by(name="John Snow")
print(query.count())


SECRET_KEY = 'test_secret'

payload_data = {
    "sub": "4242",
    "name": "Jessica Temporal",
    "nickname": "Jess"
}

def generate_token(payload, secret_key):
    token = jwt.encode(
        payload=payload,
        key=secret_key,
        algorithm="HS256"
    )
    return token
