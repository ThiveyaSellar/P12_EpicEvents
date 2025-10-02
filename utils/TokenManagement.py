import click
import jwt
import os
import platform
from datetime import datetime, timezone, timedelta

from models import User


class TokenManagement:

    @staticmethod
    def create_netrc_file(machine, access_token, refresh_token, netrc_path):
        with open(netrc_path, "w") as file:
            file.write(f"machine {machine}\n")
            file.write(f"access-token {access_token}\n")
            file.write(f"refresh-token {refresh_token}\n")
        print(f"Fichier .netrc créé et informations ajoutées à {netrc_path}")

    @staticmethod
    def get_netrc_path():
        """
        Retourne le chemin complet du fichier .netrc de l'utilisateur.
        Fonctionne sur Windows, macOS et Linux.
        """
        home_dir = os.path.expanduser("~")
        netrc_path = os.path.join(home_dir, ".netrc")

        if os.path.exists(netrc_path):
            return netrc_path
        else:
            print(".netrc n'existe pas")
            return None

    @staticmethod
    def update_tokens_in_netrc(machine, access_token, refresh_token,
                               netrc_path):
        # Lire le contenu du fichier s'il existe
        lines = []
        if os.path.exists(netrc_path):
            with open(netrc_path, "r") as file:
                lines = file.readlines()

        access_token_line = ""
        refresh_token_line = ""
        # Préparer les lignes à écrire
        if access_token != "":
            access_token_line = f"  access-token {access_token}\n"
        if refresh_token != "":
            refresh_token_line = f"  refresh-token {refresh_token}\n"

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
                    lines[i] = access_token_line
                    access_updated = True
                elif lines[i].strip().startswith("refresh-token"):
                    lines[i] = refresh_token_line
                    refresh_updated = True
                i += 1

            # Ajouter les tokens manquants s'ils n'existaient pas
            insert_index = machine_index + 1
            if not access_updated:
                lines.insert(insert_index, f"  access-token {access_token}\n")
                insert_index += 1
            if not refresh_updated:
                lines.insert(insert_index,
                             f"  refresh-token {refresh_token}\n")

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

    @staticmethod
    def is_token_expired(token):
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if not exp:
                return True
            expiration = datetime.fromtimestamp(exp, tz=timezone.utc).replace(
                tzinfo=None)
            return expiration < datetime.now()
        except jwt.DecodeError:
            return True

    @staticmethod
    def get_tokens_from_netrc(machine, netrc_path):

        if not os.path.exists(netrc_path):
            return None, None

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

    @staticmethod
    def get_token():
        netrc_path = TokenManagement.get_netrc_path()
        access_token, refresh_token = TokenManagement.get_tokens_from_netrc(
            "127.0.0.1",
            netrc_path
        )
        if access_token and refresh_token:
            # Vérifier la validité des tokens
            if TokenManagement.is_token_expired(access_token):
                return refresh_token
            else:
                return access_token
        return None

    @staticmethod
    def generate_token(payload, secret):
        token = jwt.encode(
            payload=payload,
            key=secret,
            algorithm="HS256"
        )
        return token

    @staticmethod
    def generate_tokens(user, secret):

        payload_access = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(minutes=5)
        }
        payload_refresh = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(minutes=10)
        }
        access_token = TokenManagement.generate_token(
            payload_access,
            secret
        )
        refresh_token = TokenManagement.generate_token(
            payload_refresh,
            secret
        )
        return access_token, refresh_token

    @staticmethod
    def get_user_from_access_token(access_token, secret, session):
        try:
            payload = jwt.decode(
                access_token,
                secret,
                algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            user = session.get(User, user_id)
            return user
        except jwt.ExpiredSignatureError:
            click.echo("Token expiré.")
            return None
        except jwt.InvalidTokenError:
            click.echo("Token invalide.")
            return None

    @staticmethod
    def checking_user_connection(session, secret):
        # Nom du serveur ou domaine
        machine = "127.0.0.1"
        # Chemin du fichier .netrc
        netrc_path = TokenManagement.get_netrc_path()
        connected = False
        # Chercher les tokens dans le fichier
        access_token, refresh_token = TokenManagement.get_tokens_from_netrc(
            machine,
            netrc_path
        )

        # Si pas de token, pas connecté et pas d'utilisateur
        if not access_token or not refresh_token:
            return connected, None

        # Si token d'accès valide, utilisateur connecté
        # Récupération des données utilisateurs dans le token
        if not TokenManagement.is_token_expired(access_token):
            # Récupérer les informations de l'utilisateur dans le jeton d'accès
            user = TokenManagement.get_user_from_access_token(
                access_token,
                secret,
                session
            )
            connected = True
            return connected, user

        # Si token de rafraichissement valide, générer de nouveaux tokens
        if not TokenManagement.is_token_expired(refresh_token):
            # Récupération des données utilisateurs dans le token
            user = TokenManagement.get_user_from_access_token(
                refresh_token, secret, session
            )
            # Générer de nouveaux tokens
            access_token, refresh_token = TokenManagement.generate_tokens(
                user,
                secret
            )
            TokenManagement.update_tokens_in_netrc(
                machine,
                access_token,
                refresh_token,
                netrc_path
            )
            connected = True
            return connected, user

        return connected, None

    @staticmethod
    def get_connected_user(session, secret):
        """
        L'utilisateur est connecté, on veut l'objet lié
        """
        machine = "127.0.0.1"
        netrc_path = TokenManagement.get_netrc_path()
        access_token, refresh_token = TokenManagement.get_tokens_from_netrc(
            machine, netrc_path)
        user = TokenManagement.get_user_from_access_token(access_token,
                                                          secret, session)
        return user
