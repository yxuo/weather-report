"""Main script for data server"""

import argparse

from data_service.app.data_service import DataService
from report_generator.app.report_args import ReportArgs
from report_generator.app.report_pdf import ReportPdf

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

    # region args

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
        # pdf = ReportPdf(self.args.json_data,self.args.)

    def _print_error(self, message):
        print(f"error: {message}")


if __name__ == "__main__":
    report_generator = ReportGenerator()
    # if args.detach:
    #     run_detach()
    # else:
    #     server.start_server()
