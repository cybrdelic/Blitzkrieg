import questionary
from ..cli.ui import show_spinner, print_message, print_success, show_progress

def get_project_name():
        project_name = questionary.text("Enter your project name:").ask()
        print_success(f"Project name set as {project_name}.")
        return project_name

def get_postgres_password():
        password = questionary.password("Enter a secure password for PostgreSQL:").ask()
        print_success("PostgreSQL password set.")
        return password

def get_persistence_choice():
    choice = questionary.select("Do you want to ensure data persistence across container restarts?", choices=["Yes", "No"]).ask()
    print_success(f"Data persistence choice set as {choice}.")
    return choice


def get_pgadmin_credentials(postgres, db_name):
    with show_spinner("Checking for existing admin user..."):
        if postgres.admin_user_exists(db_name):
            email = postgres.get_admin_email(db_name)
            if email:  # Ensure the email is not None
                print_success(f"Using existing admin user with email {email}")
                # You shouldn't retrieve the actual password. Here's a placeholder token.
                # In a real-world scenario, this would be a hashed password or token.
                password_token = "0101"
                return email, password_token

    # If we reach this point, it means there's no existing admin user or there was an issue fetching the email.
    print_message("No existing admin user found.")
    email = questionary.text("Enter an email for pgAdmin:").ask()
    password = questionary.password("Enter a password for pgAdmin:").ask()
    return email, password
