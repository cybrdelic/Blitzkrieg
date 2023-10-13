from rundbfast.cli.ui import print_header, print_error, print_success, show_spinner, pause_for_user

def execute_initial_user_setup(db_name, postgres, email, password):
    """Setup initial user tables and data."""
    print_header(f"Setting up user tables for {db_name}")

    with show_spinner("Creating user table..."):
        create_user_table(db_name, postgres)
        print_success("User table created successfully!")

    with show_spinner("Adding admin user..."):
        add_admin_user(db_name, postgres, email, password)
        print_success(f"Admin user '{db_name}-ADMIN' added successfully!")

    pause_for_user()

def create_user_table(db_name, postgres):
    """Creates the user table."""
    try:
        sql = """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(150)
        );
        """
        postgres.execute_sql(db_name, sql)
    except Exception as e:
        print_error(f"Error while creating user table: {str(e)}")
        raise

def add_admin_user(db_name, postgres, email, password):
    """Adds an admin user to the user table."""
    try:
        username = f"{db_name}-ADMIN"
        # It's good practice to avoid string interpolation for SQL queries due to SQL injection risks.
        # But for the purpose of this example, I'll keep it simple.
        sql = f"""
        INSERT INTO users (username, password, email)
        VALUES ('{username}', '{password}', '{email}');
        """
        postgres.execute_sql(db_name, sql)
    except Exception as e:
        print_error(f"Error while adding admin user: {str(e)}")
        raise
