"""Main script for data server"""

import argparse
from datetime import datetime
import re
from typing import List
from dateutil import parser as date_parser

from data_service.app.server import DataService

server = DataService()


class ReportGenerator:
    """Report Generator"""

    verbose:bool
    phones: List[str]
    date: str
    send_email: bool
    raw_path: str

    def __init__(self, verbose=None) -> None:
        self.verbose = verbose

    def parse_args(self) -> Exception | None:
        """Read, treat and store args"""
        try:
            args = self._parse_args()
            self._store_args(args)
        except argparse.ArgumentTypeError as arg_exc:
            if not self.verbose:
                self._print_error(arg_exc)
                return
            raise arg_exc

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

        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help="(debug) Exibe traceback de erros junto com as mensagens de erro",
            required=False,
        )

        args = parser.parse_args()

        if self.verbose is None:
            self.verbose = args.verbose
        print(args.verbose)

        return args

    def _parse_arg_date(self, date_str: str) -> datetime:
        """Validate and Parse date string into datetime object"""

        invalid_date_msg = f"parâmetro DATA tem formato inválido: '{date_str}'\n" +\
            "(esperava yyyy:mm:dd hh:MM ou yyyy:mm:dd hh:MM:ss.uu)"

        # validate
        if len(date_str) < 16:
            raise argparse.ArgumentTypeError(invalid_date_msg)

        date_regex = re.compile(
            r'^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2})'
            r'(?:[T\s](?P<hour>\d{2}):(?P<minute>\d{2})'
            r'(?:[:](?P<second>\d{2}))?)?)?)?$'
        )
        match = date_regex.match(date_str)
        if not match:
            raise argparse.ArgumentTypeError(invalid_date_msg)

        date_parts = {key: int(value) if value is not None else 0
                      for key, value in match.groupdict().items()}
        required_parts = ['year', 'month', 'day', 'hour', 'minute']
        for key in required_parts:
            if date_parts[key] == 0:
                raise argparse.ArgumentTypeError(invalid_date_msg)

        # parse
        try:
            return date_parser.parse(date_str)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(invalid_date_msg) from exc

    def _store_args(self, args: argparse.Namespace):
        self.phones: List[str] = args.TELEFONE.split(',')
        self.date: str = self._parse_arg_date(args.DATA)
        self.send_email: bool = args.envia_email
        self.raw_path: str = args.bruto

        print(self.date)

    def _print_error(self, message):
        print(f"error: {message}")

    # def read_file()


if __name__ == "__main__":
    report_generator = ReportGenerator()
    # if args.detach:
    #     run_detach()
    # else:
    #     server.start_server()
