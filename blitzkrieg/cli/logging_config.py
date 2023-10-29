import inspect
import logging
from rich.console import Console
from functools import wraps
import types


def setup_logging():
    logging.basicConfig(filename='blitzkrieg_backend.log', level=logging.INFO)
    backend_logger = logging.getLogger('backend')

    ui_logger = logging.getLogger('ui')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    ui_logger.addHandler(console_handler)

    console = Console()

    return backend_logger, ui_logger, console

def logger_decorator(backend_logger, func):
    async def wrapper(*args, **kwargs):
        backend_logger.info(f"Entering {func.__name__}")
        result = await func(*args, **kwargs)
        backend_logger.info(f"Exiting {func.__name__}")
        return result
    return wrapper

def apply_decorator_to_all_functions_in_module(module, decorator):
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) or inspect.iscoroutinefunction(obj):
            setattr(module, name, decorator(obj))

def apply_logger_to_all_functions(backend_logger):
    current_module = types.ModuleType(__name__)
    for attr_name, attr_value in globals().items():
        if callable(attr_value):
            decorated_func = logger_decorator(backend_logger, attr_value)
            setattr(current_module, attr_name, decorated_func)
