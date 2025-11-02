from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from models.bom import BOMRepository
from dialogs import BOMDialog, ConfirmDialog
from .bom_calculator_dialog import BOMCalculatorDialog

class BOMView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/BOMView.ui", self)
        
        # Connect buttons for CRUD operations
        self.btn_addBOM.clicked.connect(self.add_bom)
        self.btn_editBOM.clicked.connect(self.edit_bom)
        self.btn_deleteBOM.clicked.connect(self.delete_bom)
        
        # Connect buttons for filtering and calculator
        self.btn_show.clicked.connect(self.on_filter_clicked)
        self.btn_calculate_requirements.clicked.connect(self.show_calculator)
        
        # Load products to filter cb
        from models.product import ProductRepository
        products = ProductRepository.get_all_products()
        self.cbProductFilter.addItem("All", None)
        for p in products:
            self.cbProductFilter.addItem(p.name, p.id)
        # Load all BOM entries initially
        self.load_bom()
        
        
    # Opens the BOM calculator dialog
    def show_calculator(self):
        dialog = BOMCalculatorDialog()
        dialog.exec()
        
        
    # Emits info when the view is loaded
    def load_view(self):
        self.statusMessage.emit("BOM view loaded!", "info")
        
        
    # Loads BOM entries into the table. If product_id is provided, filters the entries.
    def load_bom(self, product_id=None):
        self.tableBOM.setRowCount(0)

        from models.product import ProductRepository
        from models.material import MaterialRepository

        all_bom = BOMRepository.get_all_bom()

        # Filter BOM by selected product if needed
        if product_id:
            all_bom = [b for b in all_bom if b.product_id == product_id]


        # Populate the table with BOM entries
        for bom_entry in all_bom:
            row = self.tableBOM.rowCount()
            self.tableBOM.insertRow(row)

            product = ProductRepository.get_product_by_id(bom_entry.product_id)
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)

            product_display = f"{product.id}. {product.name}" if product else f"#{bom_entry.product_id}"
            material_display = f"{material.id}. {material.name} ({material.unit})" if material else f"#{bom_entry.material_id}"

            self.tableBOM.setItem(row, 0, QTableWidgetItem(str(bom_entry.id)))
            self.tableBOM.setItem(row, 1, QTableWidgetItem(product_display))
            self.tableBOM.setItem(row, 2, QTableWidgetItem(material_display))
            self.tableBOM.setItem(row, 3, QTableWidgetItem(str(bom_entry.quantity_needed)))
    
    
    
    # Adds a new BOM entry via BOMDialog.
    def add_bom(self):
        dialog = BOMDialog()
        if dialog.exec():  # clicked save
            new_bom = dialog.get_bom()
            BOMRepository.add_bom(new_bom)
            self.load_bom() # reload
            self.statusMessage.emit("BOM added successffuly!", "success")
    
    
    # Edits the selected BOM entry. Shows error if no row is selected.        
    def edit_bom(self):
        selected_rows = self.tableBOM.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a BOM to edit!", "error")
            return
        
        row = selected_rows[0].row()
        bom_id = int(self.tableBOM.item(row, 0 ).text())
        bom_entry = BOMRepository.get_bom_by_id(bom_id)
    
        dialog = BOMDialog(bom_entry)
        if dialog.exec():
            updated_bom = dialog.get_bom()
            updated_bom.id = bom_entry.id
            BOMRepository.update_bom(updated_bom)
            
            self.load_bom()
            self.statusMessage.emit("BOM updated successfully!", "success")
    
    
    # Deletes the selected BOM entry after user confirmation. Shows error if no row is selected.    
    def delete_bom(self):
        selected_rows = self.tableBOM.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a BOM to delete!", "error")
            return
        
        row = selected_rows[0].row()
        bom_id = int(self.tableBOM.item(row, 0).text())
        bom_entry = BOMRepository.get_bom_by_id(bom_id)
        
        dialog = ConfirmDialog(f"Are you sure you want to delete BOM: #{bom_entry.id}?")
        if dialog.exec():  # Yes
            BOMRepository.delete_bom(bom_entry)
            self.load_bom()
            self.statusMessage.emit("BOM deleted successfully!", "success")
    
    
    
    # Applies the product filter from the cb. Reloads the table with filtered results.        
    def on_filter_clicked(self):
            product_id = self.cbProductFilter.currentData()
            self.load_bom(product_id)