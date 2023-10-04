import questionary

def get_project_name():
    return questionary.text("Enter your project name:").ask()

def get_postgres_password():
    return questionary.password("Enter a secure password for PostgreSQL:").ask()

def get_persistence_choice():
    return questionary.select("Do you want to ensure data persistence across container restarts?", choices=["Yes", "No"]).ask()

def get_pgadmin_credentials():
    email = questionary.text("Enter an email for pgAdmin:").ask()
    password = questionary.password("Enter a password for pgAdmin:").ask()
    return email, password
