from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/MainWindow.ui", self)

        self.btn_addMaterial.clicked.connect(self.add_material)

    def add_material(self):
        print("Kliknięto Add!")