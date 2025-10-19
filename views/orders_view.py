from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

class OrdersView(QWidget):
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/OrdersView.ui", self)
        
    def load_view(self):
        self.statusMessage.emit("Production orders loaded!", "info")