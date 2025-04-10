import click, jwt, os, platform
from datetime import datetime, timezone, timedelta

from models import User

def is_token_expired(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if exp:
            expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
            return expiration.replace(tzinfo=None) < datetime.now()
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

def generate_tokens(user, SECRET_KEY):

    payload_access = {
        "user_id": user.id,
        "email": user.email_address,
        "role": user.team.name,
        "exp": datetime.now() + timedelta(hours=1)
    }
    payload_refresh = {
        "user_id": user.id,
        "email": user.email_address,
        "role": user.team.name,
        "exp": datetime.now() + timedelta(hours=3)
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

def get_user_from_access_token(access_token, SECRET_KEY, session):
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

