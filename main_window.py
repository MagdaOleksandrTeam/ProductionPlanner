from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QButtonGroup, QPushButton
from views import DashboardView, MaterialView, ProductView, BOMView, MachineView, OrdersView, MRPView, ScheduleView, ReportsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # load the UI from .ui file
        uic.loadUi("ui/MainWindow.ui", self)
        # load stylesheet app.qss
        with open("styles/app.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Initialize all views
        self.dashboard_page = DashboardView()
        self.material_page = MaterialView()
        self.product_page = ProductView()
        self.bom_page = BOMView()
        self.machine_page = MachineView()
        self.orders_page = OrdersView()
        self.mrp_page = MRPView()
        self.schedule_page = ScheduleView()
        self.reports_page = ReportsView()

        # Map sidebar buttons to their pages
        self.pages = {
            self.btn_dashboard: self.dashboard_page,
            self.btn_material: self.material_page,
            self.btn_product: self.product_page,
            self.btn_bom: self.bom_page,
            self.btn_machine: self.machine_page,
            self.btn_orders: self.orders_page,
            self.btn_mrp: self.mrp_page,
            self.btn_schedule: self.schedule_page,
            self.btn_reports: self.reports_page
        }

        # Button group for exclusive selection (only one sidebar button active at a time)
        self.sidebar_group = QButtonGroup()
        self.sidebar_group.setExclusive(True)
        for btn in self.pages.keys():
            self.sidebar_group.addButton(btn)

        # Add pages to stackedWidget
        for page in self.pages.values():
            self.stackedWidget.addWidget(page)
            # Connect each page's statusMessage signal to main status bar
            page.statusMessage.connect(self.show_status)


        # Connect each sidebar button to the switch_page method
        for btn, page in self.pages.items():
            btn.clicked.connect(lambda checked, p=page: self.switch_page(p))

        # Set default page
        self.stackedWidget.setCurrentWidget(self.dashboard_page)
        self.btn_dashboard.setChecked(True)
        self.dashboard_page.load_view()
        # Initial app start message
        self.show_status("Production Planner started!", "info")
        
        
        # style non-sidebar buttons in all pages
        for page in self.pages.values():
            for btn in page.findChildren(QPushButton):
                # skip buttons from sidebar
                if not getattr(btn, "isSidebar", False):
                    btn.setStyleSheet("""
                        background-color: #3A5F8F;
                        color: white;
                        font-weight: bold;
                        border-radius: 4px;
                        padding: 6px 10px;
                    """)


    # Switches the stackedWidget to the selected page and emits the load_view msg.
    def switch_page(self, page):
        self.stackedWidget.setCurrentWidget(page)
        page.load_view()  # emit status when user switches


    # Shows a message on the status bar with a specific style based on status (info, success, warning, error)
    def show_status(self, message: str, status: str = "info", timeout: int = 5000):
        self.statusbar.setProperty("status", status)
        self.statusbar.showMessage(message, timeout)

        # Force style refresh to update colors dynamically
        QTimer.singleShot(0, lambda: self.statusbar.style().unpolish(self.statusbar))
        QTimer.singleShot(0, lambda: self.statusbar.style().polish(self.statusbar))