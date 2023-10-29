import socket

@staticmethod
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@staticmethod
def find_available_port(starting_port=5432):
    port = starting_port
    while is_port_in_use(port):
        port += 1  # try the next port
    return port
