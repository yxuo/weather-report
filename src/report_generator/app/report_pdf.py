"""report_pdf.py"""
import os
from typing import Dict, List
from datetime import datetime as dt

from PyPDF2 import PdfReader, PdfWriter  # pylint: disable=E0401
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from unidecode import unidecode  # pylint: disable=E0401


class ReportPdf:
    """
    Generate Report PDF

    Responsability:
    - Read JSON data
    - Sort data acacordingly
    - Build PDF
    - Save to file
    """
    _PAGE_WIDTH, _PAGE_HEIGHT = 200 * mm, 150 * mm
    _LEFT_MARGIN1, _RIGHT_MARGIN = 5.9 * mm, 8 * mm
    _LEFT_MARGIN2 = 2.1 * mm
    _LEFT_MARGIN = _LEFT_MARGIN1 + _LEFT_MARGIN2
    _TOP_MARGIN, _BOTTOM_MARGIN = 37 * mm, 8 * mm
    _INNER_WIDTH = _PAGE_WIDTH - _LEFT_MARGIN1 - _LEFT_MARGIN2 - _RIGHT_MARGIN
    _section: str

    def __init__(self, json_data: dict, client_name: str, report_date: str):
        self.data = json_data
        self.client_name = client_name
        self.report_date = report_date
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()

    def _create_custom_styles(self):
        custom_styles = getSampleStyleSheet()
        custom_styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        custom_styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        custom_styles.add(ParagraphStyle(
            name='Fenomeno', fontSize=11, textColor=colors.white))
        custom_styles.add(ParagraphStyle(
            name='HeaderTitle', fontSize=20, leading=26, textColor=colors.white, alignment=1))
        custom_styles.add(ParagraphStyle(
            name='ClientInfoLeft', fontSize=14, leading=12, spaceAfter=14, textColor=colors.black))
        custom_styles.add(ParagraphStyle(
            name='ClientInfoRight', fontSize=14, leading=12, spaceAfter=14,
            textColor=colors.black, alignment=TA_RIGHT, ))
        custom_styles.add(ParagraphStyle(
            name='HeaderSection', fontSize=14, leading=12, spaceAfter=14, textColor=colors.black, ))
        custom_styles.add(ParagraphStyle(
            name='Description', fontSize=11, leading=12,
            spaceAfter=14, textColor=colors.black, alignment=TA_JUSTIFY,))
        return custom_styles

    def generate_pdf(self, filename):
        """Save pdf to file"""
        # build pdfs per section (distinct headers)
        self._sort_sections()
        pdf_writer = PdfWriter()  # type: ignore
        for section, data in self.data.items():
            self._section = section
            temp_file = "$.temp.pdf"
            doc = SimpleDocTemplate(
                temp_file, pagesize=(self._PAGE_WIDTH, self._PAGE_HEIGHT),
                rightMargin=self._RIGHT_MARGIN,
                leftMargin=self._LEFT_MARGIN1,
                topMargin=self._TOP_MARGIN,
                bottomMargin=self._BOTTOM_MARGIN,
            )

            elements = []
            self._add_section(elements, data)
            doc.build(elements, onFirstPage=self._add_header,
                      onLaterPages=self._add_header)

            pdf_reader = PdfReader(temp_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        # save pdf
        with open(filename, "wb") as out:
            pdf_writer.write(out)

        # delete temp
        if os.path.exists("$.temp.pdf"):
            os.remove("$.temp.pdf")

    def _add_header(self, _canvas: canvas, doc: SimpleDocTemplate):
        """
        Create header content

        Example:
            Relatório Meteorológico
            Cliente: Joao       Data de confecção: 01/01/2024
            Análise
        """
        _canvas.saveState()

        # header
        header_title = [
            [Paragraph("<font color='white'><b>Relatório Meteorológico</b></font>",
                       self.custom_styles['HeaderTitle'])],
            [""]
        ]
        header_table = Table(
            header_title, colWidths=[self._PAGE_WIDTH], rowHeights=[13 * mm, 1.5 * mm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#073763')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ffab40')),
        ]))
        h = header_table.wrap(doc.width, doc.topMargin)[1]
        header_table.drawOn(
            _canvas, 0, self._PAGE_HEIGHT - h)

        # client info
        client_info_width = self._PAGE_WIDTH - self._LEFT_MARGIN - self._RIGHT_MARGIN
        client_info_table = Table(
            [[Paragraph("<font><b>Cliente:</b></font> Joao", self.custom_styles['ClientInfoLeft']),
              Paragraph("<b>Data de confecção:</b> 01/01/2024",
                        self.custom_styles['ClientInfoRight'])]],
            colWidths=[client_info_width/2,  client_info_width/2]
        )
        client_info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, 0), 16),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        _h = h
        h = client_info_table.wrap(doc.width, doc.topMargin)[1]
        h = _h + h + 6
        client_info_table.drawOn(
            _canvas, self._LEFT_MARGIN, self._PAGE_HEIGHT - h)

        # section
        section = Table([[Paragraph(
            f"<strong>{self._section}</strong>", self.custom_styles['HeaderSection'])]],
            colWidths=[self._INNER_WIDTH],
        )
        section.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, 0), self._LEFT_MARGIN2),
        ]))
        _h = h
        h = section.wrap(doc.width, doc.topMargin)[1]
        h = _h + h + 12
        section.drawOn(
            _canvas, self._LEFT_MARGIN, self._PAGE_HEIGHT - h)
        # elements.append(Spacer(1, 12))

    def _sort_sections(self):
        """Sort sections"""
        keys = ["Análise", "Previsão"]  # business rules
        # { normalized: original }
        normalized_keys = {unidecode(key).lower(): key for key in self.data}
        sorted_keys = []
        sorted_data = {}

        for key in keys:
            normalized_key = unidecode(key).lower()
            if normalized_key in normalized_keys:
                sorted_keys.append(normalized_keys[normalized_key])
                sorted_data[key] = self.data[normalized_keys[normalized_key]]

        self.data = sorted_data

    def _add_section(self, elements: list, entries: List[dict]):
        """
        From section group reports by `fenomeno`,
        sort them and render elements

        :example:
            ```
            <section name>  (e.g. Chuva)
            <entry 1>
            ...
            <entry N>
            <section name>  (e.g. Vento)
            <entry 1>
            ...
            ```
        """
        groups = self._group_reports(entries)
        for fenomeno, reports in groups.items():
            self._add_fenomeno(elements, fenomeno, reports)
            for report in reports:
                self._add_report(elements, report)

    def _group_reports(self, entries: List[dict]) -> Dict[str, List[dict]]:
        """
        From entries, group by "Fenomeno"

        :return:
            {[fenomeno]: entries}
        """
        # group
        groups: Dict[str, List[dict]] = {}
        for entry in entries:
            fenomeno: str = entry.get('fenomeno', 'Outros')
            if fenomeno in groups:
                groups[fenomeno].append(entry)
            else:
                groups[fenomeno] = [entry]

        # sort
        group_keys = groups.keys()
        if "Outros" in group_keys:
            # 'Outros' is the last group
            reports = groups['Outros'].copy()
            del groups['Outros']
            groups['Outros'] = reports

        return groups

    def _add_fenomeno(self, elements: list, fenomeno: str, reports: List[dict]):
        """
        Add fenomeno to pdf.

        If any report in group is `forte`, use red color.

        Example:
            [ <red> Chuva </red> ]
            2023-12-30T12:00 Registro de chuva moderada...
            2023-12-31T12:00 Registro de chuva forte...
        """
        has_forte = ["forte" in r['mensagem'].lower() for r in reports]
        if any(has_forte):
            fenomeno_color = colors.red
        else:
            fenomeno_color = colors.HexColor('#555555')
        fenomeno_table = Table(
            [[Paragraph(f"<b>{fenomeno.capitalize()}</b>",
                        self.custom_styles['Fenomeno'])]],
            colWidths=[50 * mm],
        )
        fenomeno_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), fenomeno_color),
            ('TOPPADDING', (0, 0), (-1, 0), 0.5 * mm),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 1.5 * mm),
        ]))
        fenomeno_table.hAlign = 'LEFT'
        elements.append(fenomeno_table)
        elements.append(Spacer(1, 6))

    def _add_report(self, elements: list, report: dict):
        """
        Add report content.

        Example:
            2023-12-30T12:00 Registro de chuva moderada...
        """
        data = dt.fromisoformat(report['data']).strftime(r"%d/%m/%Y às %H:%M")
        mensagem: str = report['mensagem']
        elements.append(Table([[
            "", Paragraph(f"<b>{data}</b> {mensagem}", self.custom_styles['Description'])]],
            colWidths=[self._LEFT_MARGIN2, self._INNER_WIDTH],
        ))
        elements.append(Spacer(1, 6))
