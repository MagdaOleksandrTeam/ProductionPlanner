from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from models.product import ProductRepository
from dialogs import ProductDialog, ConfirmDialog

class ProductView(QWidget):
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ProductView.ui", self)
        
        self.btn_addProduct.clicked.connect(self.add_product)
        self.btn_editProduct.clicked.connect(self.edit_product)
        self.btn_deleteProduct.clicked.connect(self.delete_product)
        
        self.load_products()
        
    def load_view(self):
        self.statusMessage.emit("Product view loaded!", "info")
        
    def load_products(self):
        self.tableProduct.setRowCount(0)
        
        products = ProductRepository.get_all_products()
        
        for product in products:
            row_position = self.tableProduct.rowCount()
            self.tableProduct.insertRow(row_position)
            self.tableProduct.setItem(row_position, 0, QTableWidgetItem(str(product.id)))
            self.tableProduct.setItem(row_position, 1, QTableWidgetItem(product.name))
            self.tableProduct.setItem(row_position, 2, QTableWidgetItem(str(product.quantity)))
            self.tableProduct.setItem(row_position, 3, QTableWidgetItem(product.unit))
            self.tableProduct.setItem(row_position, 4, QTableWidgetItem(product.description))
            
    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec():  #clicked save
            new_product = dialog.get_product()
            ProductRepository.add_product(new_product)
            self.load_products() #reload
            self.statusMessage.emit("Product added successffuly!", "success")
            
    def edit_product(self):
        selected_rows = self.tableProduct.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a product to edit!", "error")
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
        
    def delete_product(self):
        selected_rows = self.tableProduct.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a product to delete!", "error")
            return
        
        row = selected_rows[0].row()
        product_id = int(self.tableProduct.item(row, 0).text())
        product = ProductRepository.get_product_by_id(product_id)
        
        dialog = ConfirmDialog(f"Are you sure you want to delete product: '{product.name}'?")
        if dialog.exec():  # Yes
            ProductRepository.delete_product(product)
            self.load_products()
            self.statusMessage.emit("Product deleted successfully!", "success")