"""server.py"""

from logging import Logger
import logging
import os
import socket
from time import sleep

from data_service.app.handler import Handler

app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log_file = f'{app_folder}/log/data_service.log'

logging.basicConfig(
    # Defina o nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.DEBUG,
    # Formato da mensagem de log
    format='%(asctime)s [%(name)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


class DataService:
    """Data service server"""

    server_socket: socket.socket = None
    is_running = False
    host: str
    port: int
    handler: Handler

    def __init__(self, detach=False, test=False) -> None:
        self.detach = detach
        self.debug = test

        # modules
        self.handler = Handler(test)

        self._init_logger()

    def _init_logger(self):
        self.logger = logging.getLogger('DataService')
        file_handler = logging.FileHandler(
            f'{app_folder}/log/data_service.log')
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def start_server(self):
        """Start the server"""
        self.is_running = True
        self.host = '127.0.0.1'
        self.port = 5784

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.logger.info(str(f"Server listening on {self.host}:{self.port}"))

        while self.is_running:
            client_socket, addr = self.server_socket.accept()
            if not self.is_running:
                break
            data = self.handler.handle_client(client_socket, addr)

            if data == 'shutdown':
                self.stop_server()
            elif data == '_shutdown':
                self.server_socket.close()
                self.is_running = False
                self.logger.info("Stopped.")

    def stop_server(self):
        """Stop the server gracefully"""
        if self.is_running:
            self.logger.info("Stopping server...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            client.sendall(b'_shutdown')
            client.close()
            sleep(0.1)


if __name__ == "__main__":
    server = DataService()
    server.start_server()
