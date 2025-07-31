import click

class UserView:

    def success_message(self, first_name, last_name):
        click.echo(f"Inscription réussie pour {first_name} {last_name}.")

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
    def get_updating_co_worker(co_workers_ids):
        id = int(click.prompt("Which co_worker do you want to update ? "))
        while id not in co_workers_ids:
            id = int(click.prompt("Which co_worker do you want to update ? "))
        return id

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
            click.prompt("New sale rep id", default=str(default_id)))
        while team_id not in valid_ids:
            click.echo("Invalid ID. Please choose a valid ID from the list.")
            team_id = str(click.prompt("New sale rep id",
                                           default=str(default_id)))
        return int(team_id)

    @staticmethod
    def ask_change_team(co_worker, teams):
        choice = click.prompt(
            "Do you want change the team of the co-worker ? [Yes/No]")
        while choice.lower() not in ['yes', 'no', 'y', 'n']:
            choice = click.prompt(
                "Do you want change the team of the co-worker ? [Yes/No]")
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