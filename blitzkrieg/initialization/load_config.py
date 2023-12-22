from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv('config.env')


def load_config():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    return email, password
