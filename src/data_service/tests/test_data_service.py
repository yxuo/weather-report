import csv
import os
import socket
import sys
import threading
import unittest
from time import sleep

__import_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(__import_dir)

from app.server import DataServer


class TestDataService(unittest.TestCase):
    """Test data_service"""

    def setUp(self):
        self.server = DataServer()
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.start()

        self.host = '127.0.0.1'
        self.port = 5784
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        sleep(0.01)

        # Clear CSV file before each test
        self.csv_file = 'data_service/data/data.csv'
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def tearDown(self):
        self.client.close()
        self.server.stop_server()
        if self.server_thread.is_alive():
            self.server_thread.join()

    def test_shutdown_command(self):
        """Server must shut down upon receiving a command"""
        self.client.sendall(b'shutdown')
        response = self.client.recv(1024).decode()
        print('post sleep')
        self.assertEqual(response, 'Shutting down server')

    def test_valid_data(self):
        """Valid data must be processed and saved successfully"""
        valid_data = 'joao,joao@nimbusmeteorologia.com.br,01234567891,30'
        self.client.sendall(valid_data.encode())
        response = self.client.recv(1024).decode()
        self.assertEqual(response, 'Ok')

        # Verify data is saved to CSV
        with open(self.csv_file, 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0], ['joao', 'joao@nimbusmeteorologia.com.br', '01234567891', '30'])

    def test_invalid_data(self):
        """Invalid data must be rejected with an error response"""
        invalid_data = 'invalid,data'
        self.client.sendall(invalid_data.encode())
        response = self.client.recv(1024).decode()
        self.assertEqual(response, 'Error: Invalid data format')


if __name__ == '__main__':
    unittest.main()
