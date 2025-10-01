from models.base import Base
from models import Team

import click
import pytest
from commands.auth import register_auth_commands
from commands.common import register_common_commands
from commands.sales_rep import register_sales_rep_commands

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)
SessionLocal = sessionmaker(bind=engine)


def create_test_db():
    # Crée les tables dans la base en mémoire
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def cli():
    @click.group()
    def cli_group():
        pass
    register_auth_commands(cli_group)
    register_common_commands(cli_group)
    register_sales_rep_commands(cli_group)
    return cli_group


@pytest.fixture
def database():
    create_test_db()
    yield


@pytest.fixture
def db_session(database):
    session = SessionLocal()
    sales_team = Team(name="Sales")
    management_team = Team(name="Management")
    support_team = Team(name="Support")
    session.add(sales_team)
    session.add(management_team)
    session.add(support_team)
    session.commit()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
