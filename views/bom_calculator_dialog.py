from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from models.product import ProductRepository
from models.bom import BOMRepository
from models.material import MaterialRepository

class BOMCalculatorDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/BOMCalculatorDialog.ui", self)

        products = ProductRepository.get_all_products()
        for p in products:
            self.cbProductSelect.addItem(p.name, p.id)

        self.btn_calculate.clicked.connect(self.calculate)
        self.btn_close.clicked.connect(self.close)

    def calculate(self):
        product_id = self.cbProductSelect.currentData()
        quantity = self.sbQuantity.value()

        product_bom = BOMRepository.get_bom_by_product_id(product_id)

        # calculate materials
        materials_needed = {}
        for b in product_bom:
            materials_needed[b.material_id] = b.quantity_needed * quantity

        # return table
        self.twResults.setRowCount(0)
        for mat_id, qty in materials_needed.items():
            material = MaterialRepository.get_material_by_id(mat_id)
            if material:
                row = self.twResults.rowCount()
                self.twResults.insertRow(row)
                self.twResults.setItem(row, 0, QTableWidgetItem(f"{material.name} ({material.unit})"))
                self.twResults.setItem(row, 1, QTableWidgetItem(str(qty)))