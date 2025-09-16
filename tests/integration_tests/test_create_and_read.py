from click.testing import CliRunner
from tests.integration_tests.helpers import create_test_user

def test_create_data_and_read_data(cli, db_session):
    runner = CliRunner()
    user = create_test_user(db_session)
    simulated_input = "\n".join([
        "John",  # first_name
        "Doe",  # last_name
        "john.doe@example.com",  # email_address
        "0123456789",  # phone
        "Woof Company"  # company
    ]) + "\n"
    # Ajouter ici un client avec la commande
    result = runner.invoke(cli, ['create-my-client'], input=simulated_input, obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result.exit_code == 0
    assert "Client has been added." in result.output
    result2 = runner.invoke(cli, [
        'list-clients'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result2.exit_code == 0
    assert "john.doe@example.com" in result2.output