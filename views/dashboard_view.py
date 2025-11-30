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
        
    def load_view(self):
        # Emit signal indicating dashboard loaded
        self.statusMessage.emit("Dashboard loaded!", "info")

    def refresh_dashboard(self):
        """Fetch KPI counts and orders overview and update the dashboard view."""
        counts = DashboardService.get_kpi_counts()

        # Update KPI labels with current numbers and icons
        self.lbl_pending_orders.setText(f"{counts['pending_label']}: {counts['pending_orders']}")
        self.lbl_orders_in_progress.setText(f"{counts['in_progress_label']}: {counts['orders_in_progress']}")
        self.lbl_completed_orders.setText(f"{counts['completed_label']}: {counts['completed_orders']}")
        self.lbl_late_orders.setText(f"{counts['late_label']}: {counts['late_orders']}")

        # Show queued orders by priority
        queued = counts['queued_orders_by_priority']
        self.lbl_priority_queue.setText(
            f"Queued orders by priority: 🔴 High: {queued[1]}, 🟡 Medium: {queued[2]}, 🟢 Low: {queued[3]}"
        )

        # Fill dashboard table with order overview
        table_data = DashboardService.get_orders_status_overview()
        self.tableDashboard.setRowCount(len(table_data))  # set number of rows

        for row_idx, row in enumerate(table_data):
            # Populate each cell in the row
            self.tableDashboard.setItem(row_idx, 0, QTableWidgetItem(str(row["order_id"])))  # Order ID
            self.tableDashboard.setItem(row_idx, 1, QTableWidgetItem(str(row["product"])))   # Product name
            self.tableDashboard.setItem(row_idx, 2, QTableWidgetItem(str(row["quantity"])))  # Quantity
            self.tableDashboard.setItem(row_idx, 3, QTableWidgetItem(str(row["priority"])))  # Priority icon
            self.tableDashboard.setItem(row_idx, 4, QTableWidgetItem(str(row["status"])))    # Status text
            self.tableDashboard.setItem(row_idx, 5, QTableWidgetItem(str(row["deadline"])))  # Deadline

        # Auto-adjust column widths to fit content
        self.tableDashboard.resizeColumnsToContents()