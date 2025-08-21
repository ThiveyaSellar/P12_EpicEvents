import click, re


def validate_email_callback(ctx, param, value):
    email = value
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise click.BadParameter("The email is not valid.")
    return email

def validate_phone_callback(ctx, param, value):
    phone = value
    pattern = r"^0[1-9](\d{2}){4}$"
    if not re.match(pattern, phone):
        raise click.BadParameter("The phone number is not valid. It must start with the digit 0 and have 10 digits.")
    return phone

def validate_name(ctx, param, value):
    name = value
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\-']+$", name):
        if param.name == "last_name":
            label = "Last name"
        elif param.name == "first_name":
            label = "First name"
        else:
            label = param.name.capitalize()
        raise click.BadParameter(f"{label} invalid")
    return name

def validate_password(password, password2):
    return password == password2

def validate_email(value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise click.BadParameter("The email is not valid.")
    return value.strip()

def validate_phone(value):
    pattern = r"^0[1-9](\d{2}){4}$"
    if not re.match(pattern, value):
        raise click.BadParameter("The phone number is not valid. It must start with the digit 0 and have 10 digits.")
    return value.strip()