from datetime import datetime

import click

class EventView:

    @staticmethod
    def show_events(events):

        row_format = "{:<10} {:<30} {:<12} {:<12} {:<50} {:<15} {:<20} {:<15} {:<15} {:<30}"

        headers = (
            "Id","Name", "Start Date", "End Date", "Address", "Attendees",
            "Client", "Support", "Contract id", "Notes"
        )
        click.echo(row_format.format(*headers))
        click.echo("-" * 150)  # longueur estimée de la ligne, à ajuster si besoin

        for event in events:
            click.echo(row_format.format(
                event.id,
                event.name,
                str(event.start_date),
                str(event.end_date),
                event.address,
                event.nb_attendees,
                event.client.company if event.client else "N/A",
                f"{event.support.first_name} {event.support.last_name}" if event.support else "N/A",
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
        # event.notes = click.prompt("Notes", default=event.notes)
        event.notes = EventView.ask_notes(event.notes)

        return event

    @staticmethod
    def select_client_for_event(client_ids):
        id = click.prompt(
            f"For which client ? {client_ids} [Enter to skip]", default="")
        if id == "":
            return
        while not id.isdigit() or int(id) not in client_ids:
            click.echo(
                "Verify the client ID. You need to create the client before the event.")
            id = click.prompt(f"For which client ? {client_ids} [Enter to skip]",
                              default=None)
            if id is None:
                return
        return int(id)

    @staticmethod
    def select_support_for_event(support_ids):
        id = click.prompt(
            f"Which support agent do you want to assign for the event? {support_ids} [Enter to skip]", default="")
        if id == "":
            return
        while not id.isdigit() or int(id) not in support_ids:
            click.echo("Verify the support Id.")
            id = click.prompt(
                f"Which support agent do you want to assign for the event? {support_ids} [Enter to skip]",
                default=None)
            if id is None:
                return
        return int(id)

    @staticmethod
    def ask_date(date_type, default=None):
        default_date = default if default else None
        while True:
            string_date = click.prompt(f"Enter a {date_type} date (YYYY-MM-DD)", default=default_date, show_default=default_date is not None)
            try:
                date_obj = datetime.strptime(string_date.strip(), "%Y-%m-%d").date()
                return date_obj
            except ValueError:
                click.echo("Invalid format, use YYYY-MM-DD (ex : 2025-08-01)")

    @staticmethod
    def ask_period():
        today = datetime.today().date()
        while True:
            starting_date = EventView.ask_date("starting")
            if starting_date < today:
                click.echo(
                    "The start date cannot be in the past. Please try again.")
                continue
            ending_date = EventView.ask_date("ending")
            if ending_date >= starting_date:
                break
            click.echo(
                "The end date must be after the start date. Please try again.")
        return starting_date, ending_date

    @staticmethod
    def ask_notes(default_notes=None):
        click.echo("Take or edit notes in the editor and close the window")
        notes = click.edit(default_notes)
        if notes is not None:
            notes = notes.strip()
            # Si inchangé, on garde l'ancien texte
            if default_notes is not None and notes == default_notes.strip():
                return default_notes.strip()
        else:
            notes = default_notes.strip() if default_notes else ""
        return notes

    @staticmethod
    def get_new_event_data():
        event = {}
        click.echo("Enter new event informations :")
        event["name"] = click.prompt("Name")
        event["start_date"], event["end_date"] = EventView.ask_period()
        event["address"] = click.prompt("Address", default="", show_default=False)
        event["nb_attendees"] = click.prompt("Number of attendees", type=int)
        event["notes"]  = EventView.ask_notes()

        return event

    @staticmethod
    def message_event_not_found():
        click.echo("Event not found.")

    @staticmethod
    def message_adding_event_failed(errors):
        click.echo("Adding event failed...")
        click.echo(errors)

    @staticmethod
    def message_updating_event_failed(errors):
        click.echo("Updating event failed...")
        click.echo(errors)

    @staticmethod
    def message_event_added():
        click.echo("New event added.")

    @staticmethod
    def message_event_updated():
        click.echo("Event updated.")
