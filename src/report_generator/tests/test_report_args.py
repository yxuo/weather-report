"""Test data_service.py"""
import os
import threading
import unittest
from time import sleep
from unittest import mock
from unittest.mock import patch

from data_service.app.data_service import DataService
from report_generator.app.report_args import ReportArgs  # pylint: disable=E0401

up = os.path.dirname

src_folder = up(up(up(__file__)))
report_gen_app = f"{src_folder}/report_generator/app"
data_svc_app = f"{src_folder}/data_service/app"
csv_file = f"{data_svc_app}/data/$.test_data.csv"
arquivo_bruto = f"{src_folder}/report_generator/tests/data/arquivo_bruto.json"
data_svc_main = f"${src_folder}/data_service/__main__.py"
builtin_open = open


def mock_open(*args, **kwargs):
    """mock open()"""
    path = str(args[0]).replace("\\", "/")
    if "data/data.csv" in path:
        return mock.mock_open(
            read_data="nome,email,telefone,idade\n"
            "joao,joao@nimbusmeteorologia2.com.br,21934567891,30\n"
            "maria,maria@nimbusmeteorologia.com.br,21934567892,31\n"
            "jose,jose@nimbusmeteorologia.com.br,21934567893,32")(*args, **kwargs)

    # unpatched version if other path
    return builtin_open(*args, **kwargs)


class TestArgs(unittest.TestCase):
    """Test args.py"""

    def setUp(self):
        self.server = DataService(test=True)
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.start()

        self.host = '127.0.0.1'
        self.port = 5784
        sleep(0.01)

        if os.path.exists(csv_file):
            os.remove(csv_file)

    def tearDown(self):
        self.server.stop_server()
        if self.server_thread.is_alive():
            self.server_thread.join()

        if os.path.exists(csv_file):
            os.remove(csv_file)

    @patch("builtins.open", mock_open)
    @patch('argparse._sys.argv',
           [data_svc_main, '21934567891,21934567892', '2024-02-02 10:12:13',
            '--bruto', arquivo_bruto])
    def test_parse_args(self):
        """Must find user by phone"""
        args = ReportArgs(True)
        args.parse_args()
        self.assertEqual(len(args.users), 2)


if __name__ == '__main__':
    unittest.main()
