"""Main script for data server"""

from report_generator.app.report_generator import ReportGenerator  # pylint: disable=E0401,E0611

if __name__ == "__main__":
    report = ReportGenerator()
    report.parse_args()
    report.generate_pdf()
