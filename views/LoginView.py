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


