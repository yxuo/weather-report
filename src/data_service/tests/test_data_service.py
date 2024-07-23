"""Test data_service.py"""
import csv
import json
import os
import socket
import threading
import unittest
from time import sleep
from unittest.mock import mock_open, patch

from data_service.app.data_service import DataService


app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file = f"{app_folder}/data/$.test_data.csv"


class TestDataService(unittest.TestCase):
    """Test data_service"""

    def setUp(self):
        self.server = DataService(test=True)
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.start()

        self.host = '127.0.0.1'
        self.port = 5784
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        sleep(0.01)

        if os.path.exists(csv_file):
            os.remove(csv_file)

    def tearDown(self):
        self.client.close()
        self.server.stop_server()
        if self.server_thread.is_alive():
            self.server_thread.join()

        if os.path.exists(csv_file):
            os.remove(csv_file)

    def test_shutdown_command(self):
        """Server must shut down upon receiving a command"""
        # act
        self.client.sendall(b'shutdown')
        response = self.client.recv(1024).decode()
        # assert
        self.assertEqual(response, 'Shutting down server')

    def test_valid_data(self):
        """Valid data must be processed and saved successfully"""
        # arrange
        valid_data = 'joao,joao@nimbusmeteorologia.com.br,01234567891,30'

        # act
        self.client.sendall(
            json.dumps({'command': 'post', 'data': valid_data}).encode())
        response = self.client.recv(1024).decode()

        # assert
        self.assertEqual(response, 'Ok')

        # if data is saved to CSV
        with open(csv_file, 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)  # header + new item
            self.assertEqual(
                rows[1], ['joao', 'joao@nimbusmeteorologia.com.br', '01234567891', '30'])

    def test_invalid_data(self):
        """Invalid data must be rejected with an error response"""
        # arrange
        invalid_data = 'invalid,data'
        # act
        self.client.sendall(invalid_data.encode())
        response = self.client.recv(1024).decode()
        # assert
        self.assertEqual(response, 'Error: Invalid data format')

    @patch("builtins.open", new_callable=mock_open, read_data="nome,email,telefone,idade\n"
           "joao,joao@nimbusmeteorologia2.com.br,01234567891,30\n"
           "maria,maria@nimbusmeteorologia.com.br,01234567892,31\n"
           "jose,jose@nimbusmeteorologia.com.br,01234567893,32"
           )
    def test_find_data(self, _):
        """Should find data and return result"""
        # act
        self.client.sendall(
            json.dumps({'command': "get", 'phone': ["01234567891", "01234567892"]}).encode())
        response = self.client.recv(1024).decode()
        # assert
        json_data = json.loads(response)['data']
        self.assertEqual(len(json_data), 2)
        self.assertDictEqual(
            json_data[0], {
                "name": "joao",
                "email": "joao@nimbusmeteorologia2.com.br",
                "phone": "01234567891",
                "age": "30",
            })
        self.assertDictEqual(
            json_data[1], {
                "name": "maria",
                "email": "maria@nimbusmeteorologia.com.br",
                "phone": "01234567892",
                "age": "31",
            })


if __name__ == '__main__':
    unittest.main()
