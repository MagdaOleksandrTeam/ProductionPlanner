from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QButtonGroup, QPushButton
from views import DashboardView, MaterialView, ProductView, BOMView, MachineView, OrdersView, MRPView, ScheduleView, ReportsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/MainWindow.ui", self)
        with open("styles/app.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.dashboard_page = DashboardView()
        self.material_page = MaterialView()
        self.product_page = ProductView()
        self.bom_page = BOMView()
        self.machine_page = MachineView()
        self.orders_page = OrdersView()
        self.mrp_page = MRPView()
        self.schedule_page = ScheduleView()
        self.reports_page = ReportsView()

        # Map buttons to pages
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

        # Button group for exclusive selection
        self.sidebar_group = QButtonGroup()
        self.sidebar_group.setExclusive(True)
        for btn in self.pages.keys():
            self.sidebar_group.addButton(btn)

        # Add pages to stackedWidget
        for page in self.pages.values():
            self.stackedWidget.addWidget(page)
            page.statusMessage.connect(self.show_status)

        for btn, page in self.pages.items():
            btn.clicked.connect(lambda checked, p=page: self.switch_page(p))

        # default page
        self.stackedWidget.setCurrentWidget(self.dashboard_page)
        self.btn_dashboard.setChecked(True)
        self.dashboard_page.load_view()
                # Initial app start message
        self.show_status("Production Planner started!", "info")
        
        for page in self.pages.values():
            for btn in page.findChildren(QPushButton):
            # jeśli nie jest sidebar
                if not getattr(btn, "isSidebar", False):
                    btn.setStyleSheet("""
                        background-color: #3A5F8F;
                        color: white;
                        font-weight: bold;
                        border-radius: 4px;
                        padding: 6px 10px;
                    """)


    def switch_page(self, page):
        self.stackedWidget.setCurrentWidget(page)
        page.load_view()  # emit status when user switches

    def show_status(self, message: str, status: str = "info", timeout: int = 5000):
        self.statusbar.setProperty("status", status)
        self.statusbar.showMessage(message, timeout)

        # Full style reload to update colors
        QTimer.singleShot(0, lambda: self.statusbar.style().unpolish(self.statusbar))
        QTimer.singleShot(0, lambda: self.statusbar.style().polish(self.statusbar))