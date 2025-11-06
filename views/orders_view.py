from PyQt6 import uic, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from models.product import ProductRepository
from models.machine import MachineRepository
from models.order import ProductionOrder, ProductionOrderRepository
from dialogs import OrderDialog, OrderDetailsDialog, ConfirmDialog

class OrdersView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/OrdersView.ui", self)
        
        # Connect buttons
        #self.btn_show_all.clicked.connect(self.show_all)
        #self.btn_show_in_queue.clicked.connect(self.show_in_queue)
        #self.btn_show_in_progress.clicked.connect(self.show_in_progress)
        #self.btn_show_completed.clicked.connect(self.show_completed)
        #self.btn_search.clicked.connect(self.search)
        #self.btn_calculate_time.clicked.connect(self.calculate_time)
        
        # Connect CRUD buttons
        self.btn_addOrder.clicked.connect(self.add_order)
        self.btn_editOrder.clicked.connect(self.edit_order)
        self.btn_deleteOrder.clicked.connect(self.delete_order)
        
        self.load_orders()    
        self.tableOrders.itemDoubleClicked.connect(self.show_order_details)
        
        
    def load_view(self):
        self.statusMessage.emit("Production orders loaded!", "info")
        
        
    def load_orders(self):
        # Loading orders to the table
        self.tableOrders.setRowCount(0)
        orders = ProductionOrderRepository.get_all_orders()

        for order in orders:
            row = self.tableOrders.rowCount()
            self.tableOrders.insertRow(row)
            product = ProductRepository.get_product_by_id(order.product_id)
            machine = MachineRepository.get_machine_by_id(order.assigned_machine_id)

            self.tableOrders.setItem(row, 0, QTableWidgetItem(str(order.id)))
            self.tableOrders.setItem(row, 1, QTableWidgetItem(product.name if product else "-"))
            self.tableOrders.setItem(row, 2, QTableWidgetItem(machine.name if machine else "-"))
            self.tableOrders.setItem(row, 3, QTableWidgetItem(str(order.quantity)))
            self.tableOrders.setItem(row, 4, QTableWidgetItem(order.deadline))
            self.tableOrders.setItem(row, 5, QTableWidgetItem(order.status))

            # Create single priority item, put it in the table and set color
            priority_value = int(order.priority)
            priority_item = QTableWidgetItem(str(priority_value))
            self.tableOrders.setItem(row, 6, priority_item)

            # Color mapping: 1 = High, 2 = Medium, 3 = Low
            if priority_value == 1: # high
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#ff4d4d")))
            elif priority_value == 2: # medium
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#ffe066")))
            else: # low
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#66ff99")))
    
    
    def add_order(self):
    # Adding new order to db
        dialog = OrderDialog()
        if dialog.exec():
            new_order = dialog.get_order()
            ProductionOrderRepository.add_order(new_order)
            self.load_orders()
            
            
    def edit_order(self):
    # Edits order, if row not selected, returns warning
        selected_rows = self.tableOrders.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select an order to edit!", "warning")
            return

        row = selected_rows[0].row()
        order_id = int(self.tableOrders.item(row, 0).text())
        order = ProductionOrderRepository.get_order_by_id(order_id)

        dialog = OrderDialog(order)
        if dialog.exec():
            updated_order = dialog.get_order()
            updated_order.id = order.id
            ProductionOrderRepository.update_order(updated_order)
            self.load_orders()
            
            
    def delete_order(self):
    # Delete order, if row not selected returns warning
        selected_rows = self.tableOrders.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select an order to delete!", "warning")
            return

        row = selected_rows[0].row()
        order_id = int(self.tableOrders.item(row, 0).text())
        order = ProductionOrderRepository.get_order_by_id(order_id)

        dialog = ConfirmDialog(f"Are you sure you want to delete order ID {order.id}?")
        if dialog.exec():
            ProductionOrderRepository.delete_order(order)
            self.load_orders()
            
            
    def show_order_details(self):
    # Dialog showing order details, such as assigned machine and material required
        selected_rows = self.tableOrders.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        order_id = int(self.tableOrders.item(row, 0).text())
        order = ProductionOrderRepository.get_order_by_id(order_id)

        dialog = OrderDetailsDialog(order)
        dialog.exec()