from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from services.dashboard_service import DashboardService
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

class DashboardView(QWidget):
    # Signal to send status message (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi("ui/DashboardView.ui", self)

        # Automatically refresh dashboard after loading
        self.load_view()
        self.refresh_dashboard()

        # Connect refresh button
        self.btn_refresh_dashboard.clicked.connect(self.refresh_dashboard)

    def load_view(self):
        # Emit signal indicating dashboard loaded
        self.statusMessage.emit("Dashboard loaded!", "info")

    def refresh_dashboard(self):
        """Fetch KPI counts and orders overview and update the dashboard view."""
        counts = DashboardService.get_kpi_counts()

        # Update KPI labels
        self.lbl_pending_orders.setText(f"{counts['pending_label']}: {counts['pending_orders']}")
        self.lbl_orders_in_progress.setText(f"{counts['in_progress_label']}: {counts['orders_in_progress']}")
        self.lbl_completed_orders.setText(f"{counts['completed_label']}: {counts['completed_orders']}")
        self.lbl_late_orders.setText(f"{counts['late_label']}: {counts['late_orders']}")

        # Confirmation that refresh works
        self.statusMessage.emit("Dashboard refreshed!", "success")

        # Update priority summary
        queued = counts['queued_orders_by_priority']
        self.lbl_priority_queue.setText(
            f"Queued orders by priority: 🔴 High: {queued[1]}, 🟡 Medium: {queued[2]}, 🟢 Low: {queued[3]}"
        )

        # Fill dashboard table
        table_data = DashboardService.get_orders_status_overview()
        self.tableDashboard.setRowCount(len(table_data))

        for row_idx, row in enumerate(table_data):
            self.tableDashboard.setItem(row_idx, 0, QTableWidgetItem(str(row["order_id"])))
            self.tableDashboard.setItem(row_idx, 1, QTableWidgetItem(str(row["product"])))
            self.tableDashboard.setItem(row_idx, 2, QTableWidgetItem(str(row["quantity"])))
            self.tableDashboard.setItem(row_idx, 3, QTableWidgetItem(str(row["priority"])))
            self.tableDashboard.setItem(row_idx, 4, QTableWidgetItem(str(row["status"])))
            self.tableDashboard.setItem(row_idx, 5, QTableWidgetItem(str(row["deadline"])))

        self.tableDashboard.resizeColumnsToContents()

        # Progress bar logic
        total_orders = (
            counts['pending_orders']
            + counts['orders_in_progress']
            + counts['completed_orders']
            + counts['late_orders']
        )

        if total_orders > 0:
            progress = int(counts['completed_orders'] / total_orders * 100)
            if progress == 0 and counts['completed_orders'] > 0:
                progress = 1   # show at least 1% if something is completed
        else:
            progress = 0

        self.progressBar.setValue(progress)
        self.progressBar.setFormat(f"{progress}% orders completed")