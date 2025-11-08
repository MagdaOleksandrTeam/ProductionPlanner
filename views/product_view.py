from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from models.product import ProductRepository
from dialogs.dialog_views import ProductDialog, ConfirmDialog

class ProductView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        # load the UI from .ui file
        uic.loadUi("ui/ProductView.ui", self)
        
        # Connect buttons to their functions
        self.btn_product_search.clicked.connect(self.search_items)
        self.btn_addProduct.clicked.connect(self.add_product)
        self.btn_editProduct.clicked.connect(self.edit_product)
        self.btn_deleteProduct.clicked.connect(self.delete_product)
        
        self.load_products()
        
    def load_view(self):
        self.statusMessage.emit("Product view loaded!", "info")
        
    # Loads all products from db to the table
    def load_products(self):
        self.tableProduct.setRowCount(0)
        products = ProductRepository.get_all_products()
        
        # Insert each products to the table
        for product in products:
            row_position = self.tableProduct.rowCount()
            self.tableProduct.insertRow(row_position)
            self.tableProduct.setItem(row_position, 0, QTableWidgetItem(str(product.id)))
            self.tableProduct.setItem(row_position, 1, QTableWidgetItem(product.name))
            self.tableProduct.setItem(row_position, 2, QTableWidgetItem(str(product.quantity)))
            self.tableProduct.setItem(row_position, 3, QTableWidgetItem(product.unit))
            self.tableProduct.setItem(row_position, 4, QTableWidgetItem(product.description))
            
            
    # Filters products based on the search query, if there is no results - emits warning
    def search_items(self):
        query = self.le_product.text().strip().lower()
        table = self.tableProduct
        total_rows = table.rowCount()
        found_rows = []

        if total_rows == 0:
            self.statusMessage.emit("No data to search.", "warning")
            return

        if not query:
            # If search field is empty, show all rows
            for row in range(total_rows):
                table.setRowHidden(row, False)
            self.statusMessage.emit("Filter cleared – showing all products.", "info")
            return

        # Search through all rows
        for row in range(total_rows):
            item = table.item(row, 1)  # by product name
            if item and query in item.text().lower():
                table.setRowHidden(row, False)
                found_rows.append(item.text())
            else:
                table.setRowHidden(row, True)

        if found_rows:
            msg = f"Found {len(found_rows)} product{'s' if len(found_rows) > 1 else ''} matching: '{query}'"
            self.statusMessage.emit(msg, "success")
        else:
            self.statusMessage.emit(f"No products found matching: '{query}'.", "warning")
    
    
    # Adds new product to db via ProductDialog
    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec():  #clicked save
            new_product = dialog.get_product()
            ProductRepository.add_product(new_product)
            self.load_products() #reload
            self.statusMessage.emit("Product added successffuly!", "success")
            
            
    # Edits selected product, if no product selected - emit msg
    def edit_product(self):
        selected_rows = self.tableProduct.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a product to edit!", "warning")
            return
        
        row = selected_rows[0].row()
        product_id = int(self.tableProduct.item(row, 0 ).text())
        product = ProductRepository.get_product_by_id(product_id)
    
        dialog = ProductDialog(product)
        if dialog.exec():
            updated_product = dialog.get_product()
            updated_product.id = product.id
            ProductRepository.update_product(updated_product)
            
            self.load_products()
            self.statusMessage.emit("Product updated successfully!", "success")
        
        
    # Deletes product from db, if no product selected - emit msg
    def delete_product(self):
        selected_rows = self.tableProduct.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a product to delete!", "warning")
            return
        
        row = selected_rows[0].row()
        product_id = int(self.tableProduct.item(row, 0).text())
        product = ProductRepository.get_product_by_id(product_id)
        
        dialog = ConfirmDialog(f"Are you sure you want to delete product: '{product.name}'?")
        if dialog.exec():  # Yes
            ProductRepository.delete_product(product)
            self.load_products()
            self.statusMessage.emit("Product deleted successfully!", "success")