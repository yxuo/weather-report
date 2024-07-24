# pylint: disable=W0702

"""args.py"""
import argparse
from datetime import datetime
import json
import logging
import os
import re
import socket
import sys
from typing import List, Literal
from xml.dom import NotFoundErr
from dateutil import parser as date_parser
import yaml

FileType = Literal["json"]
"""
Options:
    :json: json, jsonc, json5
"""

THIS_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ReportArgs:
    """
    User args for ReportGenerator

    Responsability:
    - Read script args
    - validate args
    - transform args
    - fetch client data
    """

    _verbose: bool
    _JSON_DATA_FORMATS = ["json", "jsonc", "json5"]

    CONFIG_FILE = f"{THIS_FOLDER}/app/report_generator.yaml"

    # args
    phones: List[str]
    users: List[dict]
    date: datetime
    send_email: bool
    raw_path: str
    json_data: dict
    # constants
    config: dict
    origin_email: str

    def __init__(self, verbose=None) -> None:
        self._verbose = verbose
        self.host = '127.0.0.1'
        self.port = 5784
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger('ReportArgs')

    def parse_args(self) -> Exception | None:
        """
        Read, treat and store args.

        :param kwargs: Arguments passed programmatically.
            - phones (str): TELEFONE
            - date (str): DATA
            - raw (str): BRUTO
            - send_email (bool): --envia-email
        :raises argparse.ArgumentTypeError: If the arguments are not valid and verbose is enabled.
        :return: None if parsing is successful, otherwise returns the exception.
        """
        try:
            args = self._parse_args()
            self._store_args(args)
        except argparse.ArgumentTypeError as arg_exc:
            if not self._verbose:
                self._print_error(arg_exc)
                return
            raise arg_exc

        self._load_config()

    def _parse_kwargs(self, **kwargs) -> dict:
        """Read kwargs, validate, set to class and return object"""
        # args
        keys = ['phones', 'date', 'send_email', 'raw_path']
        args_from_kwargs = {k: v for k, v in kwargs.items() if k in keys}
        if args_from_kwargs:
            return args_from_kwargs

    def _parse_args(self) -> argparse.Namespace:
        """Read args and return as object"""
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
            '--bruto',
            type=str,
            help="Caminho para o conteúdo bruto do relatório (Exemplo: /tmp/bruto.txt)",
            required=True,
        )

        parser.add_argument(
            '--envia-email',
            action='store_true',
            help="Indica se o relatório será enviado por e-mail",
            default=False,
        )

        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help="Exibe traceback de erros junto com as mensagens de erro (debug)",
            required=False,
        )

        args = parser.parse_args()

        if self._verbose is None:
            self._verbose = args.verbose

        return args

    def _load_config(self):
        """Load script config"""
        with open(self.CONFIG_FILE, 'r', encoding='utf8') as file:
            self.config = yaml.safe_load(file)
        self.origin_email = self.config['email_origem']
        if not self.origin_email and self.send_email:
            raise ValueError(
                "ENVIAR_EMAIL está ativo porém não foi encontrado 'email_origem' "
                "em 'report_generator.yaml'"
            )

    def _store_args(self, args: argparse.Namespace):
        """Save each arg into variables"""
        self.phones: List[str] = self._parse_arg_phone(args.TELEFONE)
        self.date = self._parse_arg_date(args.DATA)
        self.send_email: bool = args.envia_email
        self.raw_path: str = self._parse_arg_raw_path(args.bruto)

    def _parse_arg_date(self, date_str: str) -> datetime:
        """Validate and Parse date string into datetime object"""

        invalid_date_msg = f"parâmetro DATA tem formato inválido: '{date_str}'\n" +\
            "(exemplo: yyyy:mm:dd hh:MM, yyyy:mm:ddThh:MM:ss)"

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

    def _parse_arg_raw_path(self, raw_path: str):
        """From path read json data"""
        if not os.path.exists(raw_path):
            raise argparse.ArgumentTypeError(
                "parâmetro BRUTO possui diretório inválido")

        if raw_path.endswith(".json"):
            self.json_data = self._read_json_data(raw_path, "json")
            return raw_path
        else:
            # guess and read every format
            try:
                self.json_data = self._read_json_data(raw_path, "json")
                return raw_path
            except Exception as exc:
                raise NotFoundErr("O arquivo não possui um formato suportado: " +
                                  str(self._JSON_DATA_FORMATS)) from exc

    def _read_json_data(self, path: str, file_type: FileType) -> dict:
        if file_type == "json":
            with open(path, "r", encoding="utf8") as f:
                json_data = json.load(f)
            return json_data

        # Case in future we read other formats
        raise NotImplementedError()

    def _parse_arg_phone(self, phones: str):
        """
        Responsability:
        - validate phone ddd
        - validate phone len
        """
        # validate
        phones_list = phones.split(',')

        for i, phone in enumerate(phones_list, 1):
            print(f"{phone} vs 11 = {re.fullmatch(r'\d{11}', phone)}")
            if not re.fullmatch(r'\d{11}', phone):
                raise argparse.ArgumentTypeError(
                    f"O telefone [{i}/{len(phones_list)}] " +
                    "deve ter: DDD + Dígito '9' + 8 números")

        self._get_users(phones_list)

        return phones_list

    def _get_users(self, phones: List[str]):
        self.logger.debug(str(f'fetch user from phones{phones}'))
        self.client.connect((self.host, self.port))
        msg = json.dumps({'command': "get", 'phone': phones})
        self.client.sendall(msg.encode())
        response = self.client.recv(1024).decode()
        self.client.close()
        self.logger.debug(str(f'fetch user response: {response}'))
        response_dict = json.loads(response)
        self.users = response_dict['data']

    def _print_error(self, message):
        print(f"error: {message}")
