"""
handler.py

Responsability:
- Validate data
- Read/Write socket messages
"""
import re
import socket

from data_service.app.utils import save_data


def validate_data(data: str):
    """
    Expected data: name,email,phone,age
    Example: `joao,joao@nimbusmeteorologia.com.br,01234567891,21`
    """
    pattern = r'^[\w\s]+,[\w\.-]+@[\w\.-]+,\d+,\d+$'
    if re.match(pattern, data):
        return True
    return False


def handle_client(client_socket: socket.socket, addr: str, debug: bool):
    """Process request and send response/error"""
    buffer_size = 1024
    data = client_socket.recv(buffer_size).decode('utf-8').strip()

    if data == '_shutdown':
        client_socket.close()
        return data

    print(f"Connection from {addr}")

    if data == 'shutdown':
        client_socket.sendall(b"Shutting down server")
        client_socket.close()
        return data

    if validate_data(data):
        save_data(data, is_test=debug)
        client_socket.sendall(b"Ok")
    else:
        client_socket.sendall(b"Error: Invalid data format")

    client_socket.close()
