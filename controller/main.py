import configparser, click, datetime, jwt, os, platform
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone, timedelta

from argon2 import PasswordHasher

from models import User, Team

def create_database(db_user, db_password, db_host, db_name):
    # Créer objet de connexion sans nom de base de données pour vérifier son existence
    engine = create_engine(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}",
        echo=False
    )
    conn = engine.connect()

    # Vérifier si la base de données existe, sinon la créer
    result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
    if not result.fetchone():  # Si la base de données n'existe pas
        print(f"La base de données {db_name} n'existe pas. Création...")
        conn.execute(text(f"CREATE DATABASE {db_name}"))
    else:
        print(f"La base de données {db_name} existe déjà.")

    conn.close()

# Récupérer les infos de connexion à la base de données depuis le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

db_user = config['database']['user']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['dbname']

create_database(db_user, db_password, db_host, db_name)

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

#------------------------------------------------------------
    # JWT
#------------------------------------------------------------

"""user = User(name='John Snow', password='johnspassword')
session.add(user)
session.commit()

print(user.id)  # None
query = session.query(User).filter_by(name="John Snow")
print(query.count())"""

# Clé secrète pour signer le jeton JWT
SECRET_KEY = "nvlzhvgi476hcich90796"

#------------------------------------------------------------
    # Netrc
#------------------------------------------------------------

def is_token_expired(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if exp:
            expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
            return expiration < datetime.now(timezone.utc)
        return True
    except jwt.DecodeError:
        return True

def get_netrc_path():
    # Afficher le système d'exploitation
    os_name = platform.system()

    if os_name == "Windows":
        netrc_path = os.path.join(os.environ["USERPROFILE"], ".netrc")
    else:
        # netrc_path = os.path.join(os.environ["HOME"], ".netrc")
        pass
    return netrc_path

def get_tokens_from_netrc(machine, netrc_path):
    # Le fichier n'existe pas
    if not os.path.exists(netrc_path):
        return None, None

    # Lire le contenu du fichier
    with open(netrc_path, "r") as file:
        lines = file.readlines()

    machine_index = None
    for i, line in enumerate(lines):
        if line.strip() == f"machine {machine}":
            machine_index = i
            break

    if machine_index is not None:
        access_token, refresh_token = None, None
        i = machine_index + 1

        while i < len(lines) and not lines[i].startswith("machine "):
            if lines[i].strip().startswith("access-token"):
                access_token = lines[i].split()[1]
            elif lines[i].strip().startswith("refresh-token"):
                refresh_token = lines[i].split()[1]
            i += 1

        return access_token, refresh_token

    return None, None

def update_tokens_in_netrc(machine, access_token, refresh_token, netrc_path):
    # Lire le contenu du fichier s'il existe
    lines = []
    if os.path.exists(netrc_path):
        with open(netrc_path, "r") as file:
            lines = file.readlines()

    # Chercher la section de la machine
    machine_index = None
    for i, line in enumerate(lines):
        if line.strip() == f"machine {machine}":
            machine_index = i
            break

    if machine_index is not None:
        # Si la machine existe, mettre à jour les tokens
        i = machine_index + 1
        access_updated, refresh_updated = False, False

        while i < len(lines) and not lines[i].startswith("machine "):
            if lines[i].strip().startswith("access-token"):
                lines[i] = f"  access-token {access_token}\n"
                access_updated = True
            elif lines[i].strip().startswith("refresh-token"):
                lines[i] = f"  refresh-token {refresh_token}\n"
                refresh_updated = True
            i += 1

        # Ajouter les tokens manquants s'ils n'existaient pas
        insert_index = machine_index + 1
        if not access_updated:
            lines.insert(insert_index, f"  access-token {access_token}\n")
            insert_index += 1
        if not refresh_updated:
            lines.insert(insert_index, f"  refresh-token {refresh_token}\n")

    else:
        # ➕ Si la machine n'existe pas, l'ajouter avec les tokens
        lines.extend([
            f"\nmachine {machine}\n",
            f"  access-token {access_token}\n",
            f"  refresh-token {refresh_token}\n"
        ])
        print(f"Machine '{machine}' ajoutée avec ses tokens.")

    # Écrire les modifications dans le fichier
    with open(netrc_path, "w") as file:
        file.writelines(lines)

def get_token():
    netrc_path = get_netrc_path()
    access_token, refresh_token = get_tokens_from_netrc("127.0.0.1", netrc_path)
    if access_token and refresh_token:
        # Vérifier la validité des tokens
        if is_token_expired(access_token):
            return refresh_token
        else:
            return access_token
    return None

def generate_token(payload, secret_key):
    token = jwt.encode(
        payload=payload,
        key=secret_key,
        algorithm="HS256"
    )
    return token

def generate_tokens(user):
    payload_access = {
        "user_id": user.id,
        "email": user.email_address,
        "role": user.team.name,
        "exp": datetime.now() + timedelta(hours=3)
    }
    payload_refresh = {
        "user_id": user.id,
        "email": user.email_address,
        "role": user.team.name,
        "exp": datetime.now() + timedelta(days=30)
    }
    access_token = generate_token(payload_access, SECRET_KEY)
    refresh_token = generate_token(payload_refresh, SECRET_KEY)
    return access_token, refresh_token

def create_netrc_file(machine, access_token, refresh_token, netrc_path):
    with open(netrc_path, "w") as file:
        file.write(f"machine {machine}\n")
        file.write(f"access-token {access_token}\n")
        file.write(f"refresh-token {refresh_token}\n")
    print(f"Le fichier .netrc a été créé et les informations ajoutées à {netrc_path}")


#------------------------------------------------------------
    # Click
#------------------------------------------------------------

@click.group()
def cli():
    """Interface en ligne de commande"""
    pass

@cli.command()
def seed_teams():
    """Ajoute des équipes par défaut à la base de données."""
    default_teams = ["Commercial","Gestion","Support"]

    for team_name in default_teams:
        if not session.query(Team).filter_by(name=team_name).first():
            team = Team(name=team_name)
            session.add(team)
            click.echo(f"Équipe '{team_name}' ajoutée.")
        else:
            click.echo(f"Équipe '{team_name}' existe déjà.")

    session.commit()
    click.echo("Toutes les équipes par défaut ont été ajoutées.")

@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Votre mot de passe")
def login(email, password):
    """Commande de connexion"""

    try:
        # Vérification si le mail de l'utilisateur existe
        user = session.query(User).filter_by(email_address=email).one()

        # Permet d'hacher le mdp en version sécurisée et illisible
        # Permet de comparer avec un mdp haché stocké en base de données
        ph = PasswordHasher()
        try:
            ph.verify(user.password, password)
        except:
            click.echo("Mot de passe incorrect.")
            return

        # Génération des jetons d'accès et de rafraichissement JWT
        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(hours=3)  # Expiration dans 1h
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(days=30)
        }
        refresh_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        netrc_path = get_netrc_path()

        # Stocker le jeton dans le fichier .netrc
        # Définir le chemin du fichier .netrc dans le dossier utilisateur Windows

        # Données à écrire dans .netrc
        machine = "127.0.0.1"

        if not os.path.exists(netrc_path):
            create_netrc_file(machine, access_token, refresh_token, netrc_path)
        else:
            update_tokens_in_netrc(machine, access_token, refresh_token, netrc_path)

        # Enregistrer le refresh token dans la base de données
        user.token = refresh_token
        session.commit()

        click.echo(f"Connexion réussie.")
        click.echo(f"Bienvenue {user.first_name} {user.last_name}!")

    except NoResultFound:
        click.echo("Utilisateur introuvable.")

# Commande d'inscription
@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--password2", prompt="Confirmation de mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--first_name", prompt="Prénom", help="Votre prénom")
@click.option("--last_name", prompt="Nom", help="Votre nom")
@click.option("--phone", prompt="Numéro de téléphone", help="Votre téléphone")
@click.option("--team", type=click.Choice(["Commercial","Gestion","Support"], case_sensitive=False), prompt="Équipe", help="Votre équipe")
def register(email, password, password2, first_name, last_name, phone, team):
    """Commande d'inscription"""
    if password != password2:
        click.echo(f"Les mots de passe ne matchent pas.")
        return

    ph = PasswordHasher()
    # Hachage du mot de passe
    hashed_password = ph.hash(password)

    # Récupérer l'id de l'équipe
    team_id = session.query(Team).filter_by(name=team).one().id

    # Création de l'utilisateur
    new_user = User(
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        email_address=email,
        phone=phone,
        team_id=team_id
    )

    # Enregistrement dans la base de données
    session.add(new_user)
    session.commit()

    click.echo(f"Inscription réussie pour {first_name} {last_name}.")

def check_permissions(user, team):
    if user.get("team") == team:
        return True
    return False

def display_login_registration_menu():
    click.echo("Bienvenue !")
    choice = click.prompt(
        "Choisissez une option : 1- Connexion 2- Inscription", type=int)
    while choice not in [1, 2]:
        click.echo("Choix invalide, veuillez réessayer.")
        choice = click.prompt(
            "Choisissez une option : 1- Connexion, 2- Inscription",
            type=int
        )

    # On exécute la commande en fonction du choix de l'utilisateur
    if choice == 1:
        # Connexion
        click.echo("Vous avez choisi de vous connecter.")
        cli(["login"])  # Appel de la commande login
    elif choice == 2:
        # Inscription
        click.echo("Vous avez choisi de vous inscrire.")
        cli(["register"])  # Appel de la commande register


def get_user_from_access_token(access_token):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user = session.get(User, user_id)
        return user
    except jwt.ExpiredSignatureError:
        click.echo("Token expiré.")
        return None
    except jwt.InvalidTokenError:
        click.echo("Token invalide.")
        return None


def main():
    # Récupérer dans le fichier .netrc les tokens
    expired_session = False
    netrc_path = get_netrc_path()
    machine = "127.0.0.1"
    access_token, refresh_token = get_tokens_from_netrc(machine, netrc_path)
    if access_token and refresh_token:
        # Récupérer les informations de l'utilisateur
        user = get_user_from_access_token(access_token)
        if is_token_expired(access_token):
            print("Access token expiré.")
            if not is_token_expired(refresh_token):
                print("Refresh token valide.")
                # Générer un nouveau access token
                access_token, refresh_token = generate_tokens(user)
                update_tokens_in_netrc(machine, access_token, refresh_token, netrc_path)
            else:
                expired_session = True

    if expired_session:
        click.echo("Session expirée.")
        display_login_registration_menu()
    else:
        click.echo(f"Bienvenue {user.first_name} !")
        print(user.team.name)
        print("Continuer les requêtes.")


if __name__ == "__main__":
    # cli()
    main()
