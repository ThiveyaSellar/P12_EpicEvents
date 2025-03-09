from sqlalchemy import create_engine, text

def create_database_if_not_existent(db_user, db_password, db_host, db_name):
    # Créer objet de connexion sans nom de base de données pour vérifier son existence
    engine = create_engine(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}",
        echo=False
    )
    conn = engine.connect()

    # Vérifier si la base de données existe, sinon la créer
    result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
    # Afficher le résultat de la requête
    if not result.fetchone():  # Si la base de données n'existe pas
        print(f"La base de données {db_name} n'existe pas. Création...")
        conn.execute(text(f"CREATE DATABASE {db_name}"))
    else:
        print(f"La base de données {db_name} existe déjà.")

    conn.close()