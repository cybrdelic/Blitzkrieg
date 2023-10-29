import logging

def setup_logging():
    logging.basicConfig(filename='blitzkrieg_backend.log', level=logging.INFO)
    backend_logger = logging.getLogger('backend')

    ui_logger = logging.getLogger('ui')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    ui_logger.addHandler(console_handler)

    return backend_logger, ui_logger
