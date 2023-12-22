from blitzkrieg.networking.port_allocation import find_available_port

def get_config():
    postgres_port = find_available_port(5432)
    pgadmin_port = find_available_port(5050)
    config = {
        'password': '0101',
        'postgres_port': postgres_port,
        'pgadmin_port': pgadmin_port
    }
    return config
