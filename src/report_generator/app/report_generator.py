"""Main script for data server"""

import argparse
import os
import shutil
import smtplib
from datetime import datetime as dt
from email.message import EmailMessage
from pathlib import Path

from data_service.app.data_service import DataService
from report_generator.app.report_args import ReportArgs  # pylint: disable=E0401,E0611
from report_generator.app.report_pdf import ReportPdf  # pylint: disable=E0401,E0611
from report_generator.app.utils import get_logger  # pylint: disable=E0401,E0611

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
            shutil.rmtree(f"{app_folder}/generated")
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
        self.logger.info(f"Found {len(self.args.users)} users")
        for user in self.args.users:
            pdf = ReportPdf(self.args.json_data, user['name'], self.args.date)
            pdf_path = pdf.generate_pdf()
            self.logger.info(str(f"PDF saved to {pdf_path.rsplit('/')[-1]}"))
            if self.args.send_email:
                self._send_email(user, pdf_path)

    def _print_error(self, message):
        print(f"error: {message}")

    def _send_email(self, user: dict, pdf_path: str):
        """Send email"""
        self.logger.info(f"Sending email to {user['email']}")
        now = dt.now().strftime(r"%m/%d/%Y")

        msg = EmailMessage()
        msg['Subject'] = f"Relatório Meteorológico - {now}"
        msg['From'] = self.args.origin_email
        msg['To'] = [user['email']]

        msg.add_alternative(f"""\
        <html>
        <body>
            <h1>Relatório Meteorológico</h1>
            <p>Segue em anexo o <b>relatório meteorológico</b> para a data de hoje ({now}).</p>
            <p>Nimbus Tecnologia</p>
        </body>
        </html>
        """, subtype='html')

        # attach pdf
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application',
                               subtype='pdf', filename='relatorio_meteorologico.pdf')

        # send

        host = self.args.config['mail_host']
        port = self.args.config['mail_port']
        with smtplib.SMTP(host, port) as smtp:
            smtp.send_message(msg)
