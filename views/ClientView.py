import click

from views.UserView import UserView


class ClientView:

    @staticmethod
    def show_all_clients(clients):

        row_format = "{:<10} {:<20} {:<20} {:<35} {:<30} {:<20} {:<20}"

        headers = (
            "Id", "First Name", "Last Name", "Email", "Phone", "Company",
            "Commercial"
        )
        click.echo(row_format.format(*headers))
        click.echo("-" * 150)  # longueur estimée de la ligne, à ajuster si besoin

        for client in clients:
            click.echo(row_format.format(
                client.id,
                client.first_name,
                client.last_name,
                client.email_address,
                client.phone,
                client.company,
                f"{client.commercial.first_name} {client.commercial.last_name}" if client.commercial else "N/A",
            ))

    @staticmethod
    def get_new_client_data():
        client = {}
        click.echo("Enter new client informations :")
        client["first_name"] = click.prompt("First name")
        client["last_name"] = click.prompt("Last name")
        client["email_address"] = click.prompt("Email address")
        client["phone"] = click.prompt("Phone")
        client["company"] = click.prompt("Company name")
        return client

    @staticmethod
    def message_client_added():
        click.echo("Client has been added.")

    @staticmethod
    def message_adding_client_failed():
        click.echo("Client has not been added.")
       
    @staticmethod 
    def show_sales_clients(clients):
        row_format = "{:<5} {:<20} {:<30} {:<15} {:<20} {:<15} {:<25} {:<20}"

        headers = (
            "Id", "Name", "Email", "Phone", "Company", "Creation date",
            "Last update", "Commercial"
        )
        click.echo(row_format.format(*headers))
        click.echo("-"*150)  # longueur estimée de la ligne, à ajuster si besoin

        for client in clients:
            click.echo(row_format.format(
                client.id,
                f"{client.first_name} {client.last_name}",
                str(client.email_address),
                str(client.phone),
                client.company,
                str(client.creation_date),
                str(client.last_update),
                str(f"{client.commercial.first_name} {client.commercial.last_name}")
            ))

    @staticmethod
    def get_updating_client(client_ids):
        if not client_ids:
            click.echo("No clients.")
            return
        id = click.prompt(
            "Which client do you want to update ? [Enter to skip]", default="")
        if id == "":
            return
        while not id.isdigit() or int(id) not in client_ids:
            click.echo("Invalid id.")
            id = click.prompt(
                "Which client do you want to update ? [Enter to skip]", default="")
            if id == "":
                return
        return int(id)

    @staticmethod
    def get_client_new_data(client, sales_reps):
        if client is None:
            click.echo("client not existent, can't be updated.")
            return
        click.echo(
            "Enter new data or press [Enter] to keep the current value:")
        # Pour chaque champ, on propose la valeur actuelle
        client.first_name = click.prompt("Client first name", default=client.first_name)
        client.last_name = click.prompt("Client last name",
                                         default=client.last_name)
        client.email_address = click.prompt("Email",
                                        default=client.email_address)
        client.phone = click.prompt("Ending date", default=client.phone)
        client.company = click.prompt("Address", default=client.company)

        new_commercial_id = UserView.ask_change_sales_rep(client, sales_reps)
        client.commercial_id = new_commercial_id

        return client