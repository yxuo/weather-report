"""handler.py"""
from ast import List
import json
import logging
import re
import socket

from data_service.app.utils import get_logger, save_data, search_data


class Handler:
    """
    From requests validate, process data and returns

    Responsability:
    - Validate data
    - Process data (acts like a service)
    - Read/Write socket messages
    """

    ERR_MSG = b"Error: Invalid data format"
    test: bool

    def __init__(self, test=False):
        self.test = test
        self.logger = get_logger("Handler")

    def handle_post(self, data: dict):
        """
        Validate and parse new item

        Input:
            (example)
            ```json
            { "method": "poat", "data": "joao,joao@nimbusmeteorologia.com.br,01234567891,21" }
            ```
        """
        # validate
        new_item: str = data.get('data', None)
        pattern = r'^[\w\s]+,[\w\.-]+@[\w\.-]+,\d+,\d+$'
        is_valid = True
        if not isinstance(new_item, str) or not re.match(pattern, new_item):
            is_valid = False

        # return
        if not is_valid:
            return self.ERR_MSG

        save_data(new_item, test=self.test)
        return b"Ok"

    def handle_get(self, data: json):
        """
        Validate and parse GET data

        Input:
        ```json
        { "method": "get", "phone": ["123","456"] }
        ```

        Response:
            { "data": [<user1>, <user2>, ...] }
        """
        # validate
        phones: List[str] = data.get('phone', None)
        if phones is None:
            return self.ERR_MSG

        # process
        found = search_data(phones)
        return json.dumps({"data": found}).encode()

    def handle_client(self, client_socket: socket.socket, addr: str):
        """Process request and send response/error"""
        buffer_size = 1024
        data = client_socket.recv(buffer_size).decode('utf-8').strip()

        # special requests

        if data == '_shutdown':
            client_socket.close()
            return data

        self.logger.info(str(f"Connection from {addr}"))

        if data == 'shutdown':
            client_socket.sendall(b"Shutting down server")
            client_socket.close()
            return data

        # JSON requests

        try:
            json_data: dict = json.loads(data)
        except json.JSONDecodeError:
            client_socket.sendall(self.ERR_MSG)
            return data
        except TypeError:
            client_socket.sendall(self.ERR_MSG)
            return data

        if json_data.get('command', None) == "post":
            response = self.handle_post(json_data)
            client_socket.sendall(response)

        elif json_data.get('command', None) == "get":
            response = self.handle_get(json_data)
            client_socket.sendall(response)

        else:
            self.logger.error("Error: invalid call")
            client_socket.sendall(b"Error: invalid call")

        client_socket.close()
