import click

class EventView:

    @staticmethod
    def show_all_events(events):

        row_format = "{:<30} {:<15} {:<15} {:<30} {:<10} {:<20} {:<10} {:<10} {:<12}"

        headers = (
            "Name", "Start Date", "End Date", "Address", "Attendees",
            "Client", "Support", "Contract", "Notes"
        )
        click.echo(row_format.format(*headers))
        click.echo(
            "-" * 200)  # longueur estimée de la ligne, à ajuster si besoin

        for event in events:
            click.echo(row_format.format(
                event.name,
                str(event.start_date),
                str(event.end_date),
                event.address,
                event.nb_attendees,
                event.client.company if event.client else "N/A",
                event.support.first_name if event.support else "N/A",
                event.contract.id if event.contract else "N/A",
                event.notes
            ))

    @staticmethod
    def show_support_events(events):

        row_format = "{:<5} {:<30} {:<15} {:<15} {:<30} {:<10} {:<20} {:<10} {:<12}"

        headers = (
            "Id", "Name", "Start Date", "End Date", "Address", "Attendees",
            "Client", "Contract", "Notes"
        )
        click.echo(row_format.format(*headers))
        click.echo(
            "-" * 200)  # longueur estimée de la ligne, à ajuster si besoin

        for event in events:
            click.echo(row_format.format(
                event.id,
                event.name,
                str(event.start_date),
                str(event.end_date),
                event.address,
                event.nb_attendees,
                event.client.company if event.client else "N/A",
                event.contract.id if event.contract else "N/A",
                event.notes
            ))

    @staticmethod
    def get_updating_event(event_ids):
        id = int(click.prompt("Which event do you want to update ? "))
        while id not in event_ids:
            id = int(click.prompt("Which event do you want to update ? "))
        return id

    @staticmethod
    def get_event_new_data(event):
        if event is None:
            click.echo("Event not existent, can't be updated.")
            return
        click.echo("Enter new data or press [Enter] to keep the current value:")
        # Pour chaque champ, on propose la valeur actuelle
        event.name = click.prompt("Event name", default=event.name)
        event.start_date = click.prompt("Starting date",
                                        default=event.start_date)
        event.end_date = click.prompt("Ending date", default=event.end_date)
        event.address = click.prompt("Address", default=event.address)
        event.nb_attendees = click.prompt("Number of attendees",
                                          default=event.nb_attendees, type=int)
        event.notes = click.prompt("Notes", default=event.notes)

        return event
