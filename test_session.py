from settings import Settings
from models.user import User

settings = Settings()
session = settings.session

print("URL base SQL :", session.bind.url)

user = session.query(User).filter_by(email_address="o@o.com").first()
print("Utilisateur trouvé :", user)
