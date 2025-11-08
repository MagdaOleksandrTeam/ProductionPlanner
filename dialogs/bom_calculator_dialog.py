from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from models.product import ProductRepository
from models.bom import BOMRepository
from models.material import MaterialRepository

class BOMCalculatorDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Signal to send status msg (info, success, warning, error)
        uic.loadUi("ui/BOMCalculatorDialog.ui", self)

        # Load all products into the product cb
        products = ProductRepository.get_all_products()
        for p in products:
            self.cbProductSelect.addItem(p.name, p.id)


        # Connect buttons
        self.btn_calculate.clicked.connect(self.calculate)
        self.btn_close.clicked.connect(self.close)


    # Calculates the required materials for a selected product and a given quantity. Updates the results table.
    def calculate(self):
        product_id = self.cbProductSelect.currentData() # get selected product id
        quantity = self.sbQuantity.value() # get desired quantity to produce

        # Fetch BOM entries for this product
        product_bom = BOMRepository.get_bom_by_product_id(product_id)

        # Calculate total materials needed
        materials_needed = {}
        for b in product_bom:
            materials_needed[b.material_id] = b.quantity_needed * quantity

        # clear previous results
        self.twResults.setRowCount(0)
        
        # Populate the results table with calculated materials
        for mat_id, qty in materials_needed.items():
            material = MaterialRepository.get_material_by_id(mat_id)
            if material:
                row = self.twResults.rowCount()
                self.twResults.insertRow(row)
                self.twResults.setItem(row, 0, QTableWidgetItem(f"{material.name} ({material.unit})"))
                self.twResults.setItem(row, 1, QTableWidgetItem(str(qty)))