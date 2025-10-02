from datetime import datetime

from click.testing import CliRunner
from tests.integration_tests.helpers import create_test_user


def test_create_data_and_read_data(cli, db_session):
    runner = CliRunner()

    # Ajouter un email unique juste pour ce test
    unique_email = f"john.doe_{int(datetime.now().timestamp())}@example.com"

    simulated_input = "\n".join([
        "John",
        "Doe",
        unique_email,  # email_address unique
        "0123456789",
        "Woof Company"
    ]) + "\n"

    result = runner.invoke(
        cli,
        ['create-my-client'],
        input=simulated_input,
        obj={"session": db_session, "SECRET_KEY": "secret"}
    )
    assert result.exit_code == 0
    assert "Client has been added." in result.output

    result2 = runner.invoke(cli, [
        'list-clients'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result2.exit_code == 0
    assert unique_email in result2.output
