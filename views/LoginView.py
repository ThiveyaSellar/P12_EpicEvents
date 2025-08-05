import click

class LoginView:

    @staticmethod
    def print_password_error():
        click.echo("Mot de passe incorrect.")

    @staticmethod
    def print_welcome_message(user):
        click.echo(f"Connexion réussie.\nBienvenue {user.first_name} {user.last_name}!")

    @staticmethod
    def print_user_not_found():
        click.echo("Utilisateur introuvable.")

    @staticmethod
    def get_logout_confirmation():
        choice = ""
        while choice not in ("o", "n"):
            choice = input(
                "Confirmez-vous votre déconnexion ? (o/n) : ").strip().lower()
            if choice not in ("o", "n"):
                print("Veuillez saisir 'o' pour oui ou 'n' pour non.")

        return choice == 'o'

    @staticmethod
    def print_logged_out_message():
        click.echo("Vous êtes déconnecté.")

    @staticmethod
    def print_staying_logged_message():
        click.echo("Retour au menu.")

    @staticmethod
    def print_exit_message():
        click.echo("Fin du programme. 'python main.py' pour le relancer.")


