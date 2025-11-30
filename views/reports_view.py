from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QFileDialog
from models.report import Reports
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


class ReportsView(QWidget):
    # Signal to send status messages (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)

    def __init__(self, report_service=None):
        super().__init__()
        uic.loadUi("ui/ReportsView.ui", self)

        # Assign the report service (model)
        self.reports_service = report_service or Reports()

        # Connect buttons and combobox
        self.btn_generate_report.clicked.connect(self.generate_report)
        self.btn_export.clicked.connect(self.export_pdf)
        self.cb_report_type.currentTextChanged.connect(self.on_report_type_changed)

        # load initial filters (dates, machines, statuses)
        self._load_initial_filters()

    def load_view(self):
        """Called when the view becomes visible. Emits status message."""
        self.statusMessage.emit("Reports / Export loaded!", "info")

    def _load_initial_filters(self):
        """Load machines and statuses into comboboxes and set default dates."""
        from models.machine import MachineRepository
        machines = MachineRepository.get_all_machines()

        # Populate machine combobox
        self.cb_machine.clear()
        self.cb_machine.addItem("All", None)
        for m in machines:
            self.cb_machine.addItem(m.name, m.id)

        # Populate status combobox
        self.cb_status.clear()
        self.cb_status.addItem("All", None)
        self.cb_status.addItem("planned", "planned")
        self.cb_status.addItem("in progress", "in_progress")
        self.cb_status.addItem("completed", "completed")

        # Set default start and end dates to today
        today = QDate.currentDate()
        self.de_start_date.setDate(today)
        self.de_end_date.setDate(today)

    def on_report_type_changed(self, report_type):
        """Hide/show filters depending on report type."""
        is_orders = report_type.lower() == "orders"
        # Only show date/machine/status filters for Orders report
        self.de_start_date.setVisible(is_orders)
        self.de_end_date.setVisible(is_orders)
        self.cb_machine.setVisible(is_orders)
        self.cb_status.setVisible(is_orders)

    def generate_report(self):
        """Fetch data from the report service and fill the table."""
        report_type = self.cb_report_type.currentText()
        start_date = self.de_start_date.date().toPyDate()
        end_date = self.de_end_date.date().toPyDate()
        machine_id = self.cb_machine.currentData()
        status = self.cb_status.currentData() or None

        try:
            # Get report data from the model
            rows, columns = self.reports_service.get_report_data(
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                machine_id=machine_id,
                status=status
            )
        except Exception as e:
            self.statusMessage.emit(f"Error fetching report: {e}", "error")
            return

        # Fill table with data
        self._fill_table(rows, columns)
        self.statusMessage.emit(f"Report generated: {len(rows)} items", "success")

    def _fill_table(self, rows, columns):
        """Fill QTableWidget with the fetched data."""
        table = self.tableReportPreview
        table.clearContents()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(len(rows))

        # Populate table cells
        for row_idx, row in enumerate(rows):
            for col_idx, key in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[key])))

        # Resize columns to fit content
        table.resizeColumnsToContents()

    def export_pdf(self):
        """Export the current table to a PDF using ReportLab."""
        table = self.tableReportPreview
        if table.rowCount() == 0:
            self.statusMessage.emit("No report to export", "warning")
            return

        # Ask user for filename
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not filename:
            return

        pdf = SimpleDocTemplate(filename, pagesize=A4)
        elements = []

        # PDF styles
        styles = getSampleStyleSheet()
        # Title shows the filename at the top of PDF
        title = Paragraph(f"Report: {filename.split('/')[-1]}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Prepare table data
        data = []
        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        data.append(headers)

        for r in range(table.rowCount()):
            row_data = [table.item(r, c).text() if table.item(r, c) else "" for c in range(table.columnCount())]
            data.append(row_data)

        # Create PDF table with repeated header
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))

        elements.append(t)
        pdf.build(elements)
        self.statusMessage.emit(f"PDF exported to {filename}", "success")