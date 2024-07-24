"""Main script for data server"""

import argparse
import os
from pathlib import Path

from data_service.app.data_service import DataService
from report_generator.app.report_args import ReportArgs
from report_generator.app.report_pdf import ReportPdf
from report_generator.app.utils import get_logger

app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        self.logger = get_logger("ReportGenerator")
        self._init_folders()

    def _init_folders(self):
        Path(f"{app_folder}/log").mkdir(parents=True, exist_ok=True)
        if os.path.exists(f"{app_folder}/generated"):
            Path(f"{app_folder}/generated").rmdir()
        Path(f"{app_folder}/generated").mkdir(parents=True, exist_ok=True)
        self.logger.info("Folders cleared")


    def parse_args(self) -> Exception | None:
        """Read, treat and store args"""
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
