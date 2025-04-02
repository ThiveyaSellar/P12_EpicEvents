import click
from views.MenuView import MenuView

from controller.LoginController import LoginView

class MenuController:

    def __init__(self):
        self.view = MenuView()

    @staticmethod
    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option("--email", prompt="Email", help="Votre email")
    @click.option("--password", prompt="Mot de passe", hide_input=True,
                  help="Votre mot de passe")
    def login(email, password):
        # Commande de connexion
        # logique
        try:
            # Vérification si le mail de l'utilisateur existe
            user = session.query(User).filter_by(email_address=email).one()

            # Permet d'hacher le mdp en version sécurisée et illisible
            # Permet de comparer avec un mdp haché stocké en base de données
            ph = PasswordHasher()
            try:
                ph.verify(user.password, password)
            except:
                # affichage
                click.echo("Mot de passe incorrect.")
                return

            # Génération des jetons d'accès et de rafraichissement JWT
            payload = {
                "user_id": user.id,
                "email": user.email_address,
                "role": user.team.name,
                "exp": datetime.now() + timedelta(hours=1)
                # Expiration dans 1h
            }
            access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            payload = {
                "user_id": user.id,
                "email": user.email_address,
                "role": user.team.name,
                "exp": datetime.now() + timedelta(hours=3)
            }
            refresh_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            netrc_path = get_netrc_path()

            # Stocker le jeton dans le fichier .netrc
            # Définir le chemin du fichier .netrc dans le dossier utilisateur Windows

            # Données à écrire dans .netrc
            machine = "127.0.0.1"

            if not os.path.exists(netrc_path):
                create_netrc_file(machine, access_token, refresh_token,
                                  netrc_path)
            else:
                update_tokens_in_netrc(machine, access_token, refresh_token,
                                       netrc_path)
            # Enregistrer le refresh token dans la base de données
            user.token = refresh_token
            session.commit()

            click.echo(f"Connexion réussie.")
            click.echo(f"Bienvenue {user.first_name} {user.last_name}!")

        except NoResultFound:
            click.echo("Utilisateur introuvable.")

    def create_login_menu(self):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        self.cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user):
        while True:
            try:
                team = user.team.name
                # Print menu and get command from user input
                self.view.show_main_menu(team)
                cmd = self.view.ask_cmd_input()
                if cmd.lower() in ["exit", "quit"]:
                    break
                self.cli.main(cmd.split(), standalone_mode=False)
            except Exception as e:
                click.echo(f"Erreur : {e}")
                break