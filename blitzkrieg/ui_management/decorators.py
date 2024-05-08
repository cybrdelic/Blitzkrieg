from functools import wraps
from halo import Halo
from rich.console import Console

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

def with_spinner(message, success_message="Succeeded", failure_message="Failed", spinner='dots'):
    def spinner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Halo(text=message, spinner=spinner, color='magenta') as halo:
                try:
                    result = func(*args, **kwargs)
                    if result:
                        halo.succeed(f"{success_message}")
                    else:
                        halo.fail(f"{failure_message}")
                    return result
                except Exception as e:
                    halo.fail(f"{failure_message}: {str(e)}")
                    return False
        return wrapper
    return spinner_decorator
