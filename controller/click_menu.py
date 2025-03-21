""""import click

@click.group
def cli():
    pass

# Commande click pour demander et afficher Bonjour
@cli.command()
@click.option("--test",prompt="message", help="Votre message")
def display_message(test):
    print(test)

@cli.command()
def click_menu():
    print("-- Menu --")
    display_message()
    print("-- End --")

if __name__ == "__main__" :
    click_menu()"""

"""
import click

# Liste des tâches en mémoire (simulant une base de données)
tasks = []


@click.group()
def cli():

    pass


@cli.command()
@click.argument("task")
def add(task):

    tasks.append({"task": task, "done": False})
    click.echo(f"Tâche ajoutée : {task}")


@cli.command()
def list():

    if not tasks:
        click.echo("Aucune tâche pour le moment.")
        return

    click.echo("📋 Liste des tâches :")
    for i, task in enumerate(tasks, 1):
        status = "✅" if task["done"] else "❌"
        click.echo(f"{i}. {status} {task['task']}")


@cli.command()
@click.argument("task_number", type=int)
def complete(task_number):

    if 1 <= task_number <= len(tasks):
        tasks[task_number - 1]["done"] = True
        click.echo(f"Tâche {task_number} complétée ! ✅")
    else:
        click.echo("Numéro de tâche invalide.")


@cli.command()
@click.argument("task_number", type=int)
def delete(task_number):

    if 1 <= task_number <= len(tasks):
        removed_task = tasks.pop(task_number - 1)
        click.echo(f"Tâche supprimée : {removed_task['task']}")
    else:
        click.echo("Numéro de tâche invalide.")


if __name__ == "__main__":
    cli()
"""

import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument("nom")
def salut(nom):
    """Dit bonjour à l'utilisateur."""
    click.echo(f"Bonjour, {nom} !")

@cli.command()
@click.argument("nom")
def bye(nom):
    """Dit bonjour à l'utilisateur."""
    click.echo(f"Bye, {nom} !")

if __name__ == "__main__":
    while True:
        try:
            cmd = input("Commande > ")
            if cmd.lower() in ["exit", "quit"]:
                break
            cli.main(cmd.split(), standalone_mode=False)
        except Exception as e:
            click.echo(f"Erreur : {e}")

