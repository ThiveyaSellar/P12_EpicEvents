# P12_EpicEvents

## About this project

EpicEvents, an event consulting and management company, needs a Custom Relationship Management software to improve the organization of customer events.

## Installation

### Clone remote repository :

```
git clone https://github.com/ThiveyaSellar/P12_EpicEvents.git
```

### Create a virtual environment in the project :
```
python -m venv env
```

### Activate virtual environment :
- Linux :
```
source env/bin/activate
```

- Windows :
```
env\Scripts\activate.bat
```

### Install the necessary packages from requirements.txt :
```
pip install -r requirements.txt
```
### Install MYSQL:
Download the MySQL server and client from https://dev.mysql.com/downloads/mysql/

### Configure the project:
Fill in the config_empty.ini file with the information and rename it config.ini.

### Create the database and tables using the SQL commands in init_db.sql:
```
mysql -u root -p < init_db.sql
```

- Launch the CRM Software
```
python main.py
```

## Flake8

Flake8 is a package for checking that code complies with PEP8 guidelines.
- Configuration file : .flake8
- Generate flake 8 report :
```
flake8 > flake-report.txt
```

## Tests

- Unit tests coverage :
```
pytest --cov=controller tests/unit_tests
```
- Integration tests
```
pytest tests/integration_tests
```


