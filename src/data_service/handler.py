import re
from app.utils import save_data

def validate_data(data):
    pattern = r'^[\w\s]+,[\w\.-]+@[\w\.-]+,\d+,\d+$'
    if re.match(pattern, data):
        return True
    return False

def handle_client(client_socket):
    buffer_size = 1024
    data = client_socket.recv(buffer_size).decode('utf-8').strip()

    if validate_data(data):
        save_data(data)
        client_socket.sendall(b"Ok")
    else:
        client_socket.sendall(b"Error: Invalid data format")

    client_socket.close()
