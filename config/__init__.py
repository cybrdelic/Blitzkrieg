# rundbfast/config/__init__.py
from dotenv import load_dotenv
import os

def load_configurations():
    load_dotenv()
    return {
        "DEFAULT_PORT": os.getenv("DEFAULT_PORT"),
        "TIMEOUT": os.getenv("TIMEOUT"),
        "SLEEP_INTERVAL": os.getenv("SLEEP_INTERVAL"),
        "WAIT_AFTER_CONTAINER_START": os.getenv("WAIT_AFTER_CONTAINER_START"),
        "WAIT_AFTER_CONTAINER_REMOVE": os.getenv("WAIT_AFTER_CONTAINER_REMOVE"),
        "DOCKER_IMAGE_POSTGRES": os.getenv("DOCKER_IMAGE_POSTGRES"),
        "NETWORK_NAME": os.getenv("NETWORK_NAME")
    }
