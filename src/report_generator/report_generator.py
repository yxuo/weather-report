"""Main script for data server"""

import argparse
from typing import List

from data_service.app.server import DataService

server = DataService()


class ReportGenerator:
    """Report Generator"""

    phones: List[str]
    date: str
    send_email: bool
    raw_path: str

    def __init__(self, test=False) -> None:
        if test:
            return

        self.parse_args()

    def parse_args(self):
        """Read, treat and store args"""
        args = self._parse_args()
        self._store_args(args)

    def _parse_args(self) -> argparse.Namespace:
        """Read args, vlaidate, set to class and return object"""
        parser = argparse.ArgumentParser(
            description="Gerador de Relatórios Meteorológicos",
            add_help=True,
        )

        # read
        parser.add_argument(
            'TELEFONE',
            type=str,
            action='store',
            help="Um ou mais números de telefone separados por vírgula" +
            "(Exemplo: 01234567891,78945612348)",
        )

        parser.add_argument(
            'DATA',
            type=str,
            help="Data no formato ISO 8601 (Exemplo: 2024-01-01T00:00)",
        )

        parser.add_argument(
            '--envia-email',
            action='store_true',
            help="Indica se o relatório será enviado por e-mail",
            default=False,
        )

        parser.add_argument(
            '--bruto',
            type=str,
            help="Caminho para o conteúdo bruto do relatório (Exemplo: /tmp/bruto.txt)",
            required=True,
        )
        return parser.parse_args()

    def _store_args(self, args: argparse.Namespace):
        self.phones: List[str] = args.TELEFONE.split(',')
        self.date: str = args.DATA
        self.send_email: bool = args.envia_email
        self.raw_path: str = args.bruto

    # def read_file()


if __name__ == "__main__":
    report_generator = ReportGenerator()
    # if args.detach:
    #     run_detach()
    # else:
    #     server.start_server()
