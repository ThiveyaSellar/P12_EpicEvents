from datetime import datetime, date



def get_ids(object_list):
    return [int(obj.id) for obj in object_list]

def check_field_length(data, field, length, errors):
    if data.get(field) and len(data[field]) > length:
        errors.append(f"The {field} field is too long.")

def check_field_and_length(data, field, length, errors):
    if not data.get(field):
        errors.append(f"The {field} field is required.")
    elif len(data[field]) > length:
        errors.append(f"The {field} is too long.")

def check_email_field(data, errors):
    email = data.get("email_address") or data.get("email", "")
    if not email:
        errors.append("The email is required.")
    elif "@" not in email or len(email) > 100:
        errors.append("Email is not valid or too long.")

def check_phone_field(data, errors):
    phone = data.get("phone", "")
    if not phone:
        errors.append("The phone is required.")
    elif not phone.isdigit() or len(phone) > 12:
        errors.append("The phone is not valid or too long.")

def check_date_field(data, field, errors):
    date_value = data.get(field)
    if not date_value:
        errors.append(f"The date_value {field} is required.")
        return
    if isinstance(date_value,str):
        try:
            data[field] = datetime.strptime(date_value,"%Y-%m-%d").date()
        except ValueError:
            errors.append(f"The format of the date for {field} is not valid.")
    elif not isinstance(date_value, date):
        errors.append(f"The value of the date for {field} is not valid.")

def check_number_field(data, field, errors):
    field_value = data.get(field)
    if not field_value:
        errors.append(f"The {field} is required.")
        return
    if field_value < 0:
        errors.append(f"The value of {field} must be positive.")
        return

def check_team_field(data, errors):
    print(data)
    team = data.get("team")
    if team.lower() not in ['commercial','support','gestion']:
        errors.append("Team must either 'commercial', 'support', 'gestion'.")


