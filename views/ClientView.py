import click

class ClientView:

    @staticmethod
    def show_all_clients(clients):

        row_format = "{:<20} {:<20} {:<35} {:<30} {:<20} {:<20}"

        headers = (
            "First Name", "Last Name", "Email", "Phone", "Company",
            "Commercial"
        )
        click.echo(row_format.format(*headers))
        click.echo(
            "-" * 150)  # longueur estimée de la ligne, à ajuster si besoin

        for client in clients:
            click.echo(row_format.format(
                client.first_name,
                str(client.last_name),
                str(client.email_address),
                client.phone,
                client.company,
                client.commercial_id
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
        row_format = "{:<5} {:<30} {:<15} {:<15} {:<30} {:<10} {:<20}"

        headers = (
            "Id", "Name", "Email", "Phone", "Company", "Creation date",
            "Last update"
        )
        click.echo(row_format.format(*headers))
        click.echo(
            "-" * 200)  # longueur estimée de la ligne, à ajuster si besoin

        for client in clients:
            click.echo(row_format.format(
                client.id,
                f"{client.first_name} {client.last_name}",
                str(client.email_address),
                str(client.phone),
                client.company,
                str(client.creation_date),
                str(client.last_update)
            ))

    @staticmethod
    def get_updating_client(client_ids):
        id = int(click.prompt("Which client do you want to update ? "))
        while id not in client_ids:
            id = int(click.prompt("Which client do you want to update ? "))
        return id

    @staticmethod
    def get_client_new_data(client):
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

        return client