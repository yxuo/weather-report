"""Main script for data server"""

from report_generator.app.report_generator import ReportGenerator

if __name__ == "__main__":
    report = ReportGenerator()
    report.parse_args()
