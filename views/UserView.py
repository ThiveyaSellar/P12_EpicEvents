import click

class UserView:

    def success_message(self, first_name, last_name):
        click.echo(f"Registration is successful for {first_name} {last_name}.")

    def show_co_workers(self, co_workers):
        row_format = "{:<10} {:<30} {:<30} {:<15} {:<15}"

        headers = (
            "Id", "Name", "Email", "Phone", "Team"
        )
        click.echo(row_format.format(*headers))
        click.echo("-" * 150)  # longueur ligne estimée, à ajuster si besoin

        for co_worker in co_workers:
            click.echo(row_format.format(
                co_worker.id,
                f"{co_worker.first_name} {co_worker.last_name}",
                co_worker.email_address,
                co_worker.phone,
                co_worker.team.name
            ))

    @staticmethod
    def get_co_worker(co_workers_ids, action):
        id = click.prompt(f"Which co worker do you want to {action} ? ",type=int)
        while id not in co_workers_ids:
            id = click.prompt(f"Which co worker do you want to {action} ? ",type=int)
        return id

    @staticmethod
    def message_co_worker_not_found():
        click.echo("Co_worker not found.")

    @staticmethod
    def message_co_worker_deleted():
        click.echo("Co_worker deleted.")

    @staticmethod
    def message_email_exists():
        click.echo("An account with this email already exists.")

    @staticmethod
    def show_teams(teams, default_id):
        row_format = "{:<10} {:<40}"
        headers = (
            "Id", "Name"
        )
        click.echo(row_format.format(*headers))
        click.echo("-------------------")
        for team in teams:
            click.echo(row_format.format(
                team.id,
                f"{team.name}",
            ))
        valid_ids = [str(s.id) for s in teams]
        team_id = str(
            click.prompt("New team id", default=str(default_id)))
        while team_id not in valid_ids:
            click.echo("Invalid ID. Please choose a valid ID from the list.")
            team_id = str(click.prompt("New team id",
                                           default=str(default_id)))
        return int(team_id)

    @staticmethod
    def ask_change_team(co_worker, teams):
        choice = click.prompt(
            "Do you want to change the team of the co-worker ? [Yes/No]")
        while not choice or choice.lower() not in ['yes', 'no', 'y', 'n']:
            choice = click.prompt(
                "Do you want change to the team of the co-worker ? [Yes/No]")
        if choice.lower() in ['yes', 'y']:
            co_worker.team_id = UserView.show_teams(teams, co_worker.team_id)

    @staticmethod
    def get_co_worker_new_data(co_worker, teams):
        if co_worker is None:
            click.echo("Co_worker not existent, can't be updated.")
            return
        click.echo("Enter new data or press [Enter] to keep the current value:")
        # Pour chaque champ, on propose la valeur actuelle
        co_worker.first_name = click.prompt("First name", default=co_worker.first_name)
        co_worker.last_name = click.prompt("Last name",
                                            default=co_worker.last_name)
        co_worker.email_address = click.prompt("Email address",
                                        default=co_worker.email_address)
        co_worker.phone = click.prompt("Phone", default=co_worker.phone)
        UserView.ask_change_team(co_worker, teams)

        return co_worker

    @staticmethod
    def show_sales_reps(sales_reps, default_id):
        row_format = "{:<10} {:<40}"
        headers = (
            "Id", "Name"
        )
        click.echo(row_format.format(*headers))
        click.echo("-------------------")
        for sale_rep in sales_reps:
            click.echo(row_format.format(
                sale_rep.id,
                f"{sale_rep.first_name} {sale_rep.last_name}",
            ))
        valid_ids = [str(s.id) for s in sales_reps]
        sale_rep_id = str(
            click.prompt("Which sale rep id", default=str(default_id)))
        while sale_rep_id not in valid_ids:
            click.echo("Invalid ID. Please choose a valid ID from the list.")
            sale_rep_id = str(click.prompt("Which sale rep id",
                                           default=str(default_id)))
        return int(sale_rep_id)

    @staticmethod
    def show_sales_reps(sales_reps, default_id):
        row_format = "{:<10} {:<40}"
        headers = (
            "Id", "Name"
        )
        click.echo(row_format.format(*headers))
        click.echo("-------------------")
        for sale_rep in sales_reps:
            click.echo(row_format.format(
                sale_rep.id,
                f"{sale_rep.first_name} {sale_rep.last_name}",
            ))
        valid_ids = [str(s.id) for s in sales_reps]
        sale_rep_id = str(
            click.prompt("New sale rep id", default=str(default_id)))
        while sale_rep_id not in valid_ids:
            click.echo("Invalid ID. Please choose a valid ID from the list.")
            sale_rep_id = str(click.prompt("New sale rep id",
                                           default=str(default_id)))
        return int(sale_rep_id)

    @staticmethod
    def ask_change_sales_rep(client, sales_reps):
        choice = click.prompt(
            "Do you want to change the sale representative ? [Yes/No]")
        while not choice or choice.lower() not in ['yes', 'no', 'y', 'n']:
            choice = click.prompt(
                "Do you want change to the sale representative ? [Yes/No]")
        if choice.lower() in ['yes', 'y']:
            new_commercial_id = UserView.show_sales_reps(sales_reps,
                                                           client.commercial_id)
            return new_commercial_id
        return

    @staticmethod
    def show_my_clients(clients):
        row_format = "{:<10} {:<30} {:<20}"

        headers = (
            "Id", "Name", "Company"
        )
        click.echo(row_format.format(*headers))
        click.echo("-" * 100)

        for client in clients:
            click.echo(row_format.format(
                client.id,
                f"{client.first_name} {client.last_name}",
                client.company,
            ))

    @staticmethod
    def choose_support_collab(support_employees):
        row_format = "{:<10} {:<40}"
        headers = (
            "Id", "Name"
        )
        click.echo(row_format.format(*headers))
        click.echo("-------------------")
        for employee in support_employees:
            click.echo(row_format.format(
                employee.id,
                f"{employee.first_name} {employee.last_name}",
            ))
        valid_ids = [str(s.id) for s in support_employees]
        support_id = str(
            click.prompt("Which support co_worker do you want to add to the event ? "))
        while support_id not in valid_ids:
            click.echo("Invalid ID. Please choose a valid ID from the list.")
            support_id = str(click.prompt("Which support co_worker do you want to add to the event ? "))
        return support_id

    @staticmethod
    def message_adding_co_worker_failed(errors):
        click.echo("Co-worker has not been added.")
        if isinstance(errors, list):
            for e in errors:
                click.echo(str(e))
        else:
            click.echo(str(errors))

    @staticmethod
    def message_updating_co_worker_failed(errors):
        click.echo("Co-worker has not been updated.")
        if isinstance(errors, list):
            for e in errors:
                click.echo(str(e))
        else:
            click.echo(str(errors))

    @staticmethod
    def message_db_error(errors):
        # Affiche proprement même si errors est une liste ou autre
        if isinstance(errors, list):
            for e in errors:
                click.echo(str(e))
        else:
            click.echo(str(errors))