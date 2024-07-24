"""Main script for data server"""

import argparse
import logging
import os

from data_service.app.data_service import DataService
from report_generator.app.report_args import ReportArgs
from report_generator.app.report_pdf import ReportPdf

app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file = f'{app_folder}/log/report_generator.log'

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

server = DataService()


class ReportGenerator:
    """
    Report Generator

    Responsability:
    - get args and json data
    - generate pdf
    - 
    """

    verbose: bool

    # args
    args: ReportArgs

    def __init__(self, verbose=None) -> None:
        self.verbose = verbose
        self.logger = logging.getLogger('ReportGenerator')

    def parse_args(self) -> Exception | None:
        """Read, treat and store args"""
        print('parse args')
        self.args = ReportArgs(self.verbose)
        try:
            self.args.parse_args()
        except argparse.ArgumentTypeError as arg_exc:
            if not self.verbose:
                self._print_error(arg_exc)
                return
            raise arg_exc

    def generate_pdf(self):
        """
        For every client, generate pdf and send email
        """
        print("generate pdf")
        self.logger.debug(str(f"Users: {self.args.users}"))
        for user in self.args.users:
            pdf = ReportPdf(self.args.json_data, user['name'], self.args.date)
            pdf.generate_pdf("relatorio.pdf")

    def _print_error(self, message):
        print(f"error: {message}")


if __name__ == "__main__":
    report_generator = ReportGenerator()
    # if args.detach:
    #     run_detach()
    # else:
    #     server.start_server()
