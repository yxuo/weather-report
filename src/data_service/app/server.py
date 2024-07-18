"""server.py"""

import socket
from time import sleep

from app.handler import handle_client


class DataServer:
    """Data service server"""

    server_socket: socket.socket = None
    is_running = False
    host: str
    port: int

    def __init__(self, detach=False, debug=False) -> None:
        self.detach = detach
        self.debug = debug

    def start_server(self):
        """Start the server"""
        self.is_running = True
        self.host = '127.0.0.1'
        self.port = 5784

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while self.is_running:
            client_socket, addr = self.server_socket.accept()
            if not self.is_running:
                break
            data = handle_client(client_socket, addr, self.debug)

            if data == 'shutdown':
                self.stop_server()
            elif data == '_shutdown':
                self.server_socket.close()
                self.is_running = False
                print("Stopped.")

    def stop_server(self):
        """Stop the server gracefully"""
        if self.is_running:
            print("Stopping server...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            client.sendall(b'_shutdown')
            client.close()
            sleep(0.1)


if __name__ == "__main__":
    server = DataServer()
    server.start_server()
