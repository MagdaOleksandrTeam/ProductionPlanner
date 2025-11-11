from PyQt6 import uic, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from models.product import ProductRepository
from models.machine import MachineRepository
from models.order import ProductionOrderRepository
from dialogs.dialog_views import OrderDialog, OrderDetailsDialog, ConfirmDialog
from dialogs.order_calculator_dialog import OrderCalculatorDialog


class OrdersView(QWidget):
    """Main Orders view — shows all production orders and allows performing
    CRUD operations, filtering, searching, and production time calculation."""
    statusMessage = pyqtSignal(str, str) # Signal to send status msg (info, success, warning, error)
    
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/OrdersView.ui", self)
        
        # --- Connect filter buttons ----
        self.btn_show_all.clicked.connect(lambda: self.load_orders())
        self.btn_show_in_queue.clicked.connect(lambda: self.load_orders(status_filter="in_queue"))
        self.btn_show_in_progress.clicked.connect(lambda: self.load_orders(status_filter="in_progress"))
        self.btn_show_completed.clicked.connect(lambda: self.load_orders(status_filter="completed"))
        
        # ---- search and calculator ----
        self.btn_search.clicked.connect(self.search_orders)    
        self.btn_calculate_time.clicked.connect(self.open_order_calculator)
        
        # ---- CRUD operations ----
        self.btn_addOrder.clicked.connect(self.add_order)
        self.btn_editOrder.clicked.connect(self.edit_order)
        self.btn_deleteOrder.clicked.connect(self.delete_order)
        
        self.tableOrders.itemDoubleClicked.connect(self.show_order_details)
        
        self.load_orders()   # Initial data load
        
        self.load_product_filter()
        self.cb_filter_product.currentIndexChanged.connect(
        lambda: self.load_orders(product_filter_id=self.cb_filter_product.currentData()))
        
        
    def load_view(self):   #emit info msg
        self.statusMessage.emit("Production orders loaded!", "info")
        
        
# --------- TABLE LOADING -----------
        
    def load_orders(self, status_filter=None, search_text=None, product_filter_id=None):
    #Load orders into the table. Optional filtering by status and search text.
        self.tableOrders.setRowCount(0)
        orders = ProductionOrderRepository.get_all_orders()
        
        #Filter by order status
        if status_filter:  
            orders = [o for o in orders if o.status == status_filter]
            
        # Filter by product
        if product_filter_id is not None:
            orders = [o for o in orders if o.product_id == product_filter_id]
                
        #Filter by search query (order ID or product name)
        if search_text:    
            search_text = search_text.lower()
            orders = [o for o in orders
                      if search_text in str(o.id).lower()
                      or search_text in ProductRepository.get_product_by_id(o.product_id).name.lower()]
        
        # Populate the table
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

            # Priority value (1 = high, 2 = medium, 3 = low)
            priority_value = int(order.priority)
            
            # --- Map numeric value to string ---
            priority_text = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}.get(priority_value, "UNKNOWN")
            
            priority_item = QTableWidgetItem(priority_text)
            self.tableOrders.setItem(row, 6, priority_item)

            # Color by priority
            if priority_value == 1: # high
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#ff4d4d")))
            elif priority_value == 2: # medium
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#ffe066")))
            else: # low
                priority_item.setBackground(QtGui.QBrush(QtGui.QColor("#66ff99")))
    
    
# ----------- SEARCH ---------
    def search_orders(self):
    #Search for orders by ID or product name. Emits messages through the status bar.
        text = self.le_search.text().strip()

        if not text:
            self.load_orders()
            self.statusMessage.emit("Showing all orders.", "info")
            return

        try:
            # Search by Id
            if text.isdigit():
                order = ProductionOrderRepository.get_order_by_id(int(text))
                if order:
                    self.load_orders(search_text=str(order.id))
                    self.statusMessage.emit(f"Found order with ID {text}.", "success")
                else:
                    self.tableOrders.setRowCount(0)
                    self.statusMessage.emit(f"No order found with ID {text}.", "warning")
                
                # Search by product name
            else:
                orders = ProductionOrderRepository.get_all_orders()
                filtered = []
                for o in orders:
                    product = ProductRepository.get_product_by_id(o.product_id)
                    if product and text.lower() in product.name.lower():
                        filtered.append(o)

                if filtered:
                    self.load_orders(search_text=text)
                    self.statusMessage.emit(f"Found {len(filtered)} order(s) for '{text}'.", "success")
                else:
                    self.tableOrders.setRowCount(0)
                    self.statusMessage.emit(f"No orders found for '{text}'.", "warning")

        except Exception as e:
            self.statusMessage.emit(f"Error during search: {str(e)}", "error")
        
        
# --------- SELECT PRODUCT --------
    def load_product_filter(self):
        self.cb_filter_product.clear()
        self.cb_filter_product.addItem("All", None)
        
        products = ProductRepository.get_all_products()
        for p in products:
            self.cb_filter_product.addItem(p.name, p.id)

        # Default All
        self.cb_filter_product.setCurrentIndex(0)


    def on_product_selected(self, index):
        text = self.cb_filter_product.currentText()
        product_id = self.cb_filter_product.itemData(index)
        
        if text == "All" or product_id is None:
            self.load_orders(product_filter_id=None)  # pokaż wszystko
            self.statusMessage.emit("Showing all products", "info")
        else:
            self.load_orders(product_filter_id=product_id)
            product = ProductRepository.get_product_by_id(product_id)
            if product:
                self.statusMessage.emit(f"Selected product: {product.name}", "info")
                
# ------------ CRUD ------------
    def add_order(self):
    # Open a dialog to add a new production order.
        dialog = OrderDialog()
        if dialog.exec():
            new_order = dialog.get_order()
            ProductionOrderRepository.add_order(new_order)
            self.load_orders()
            
            
    def edit_order(self):
    # Edit the selected order (if any).
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
    # Delete the selected order after confirmation.
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
            
            
# -------- DETAILS & CALCULATOR ----------
    def show_order_details(self):
    # Open a dialog showing selected order details and required materials.
        selected_rows = self.tableOrders.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        order_id = int(self.tableOrders.item(row, 0).text())
        order = ProductionOrderRepository.get_order_by_id(order_id)

        dialog = OrderDetailsDialog(order)
        dialog.exec()
        
    def calculate_time(self):
        selected_rows = self.tableOrders.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Select an order to calculate time!", "warning")
            return

        row = selected_rows[0].row()
        order_id = int(self.tableOrders.item(row, 0).text())
        order = ProductionOrderRepository.get_order_by_id(order_id)

        
    def open_order_calculator(self):
    # Open the production time calculator dialog.
        dialog = OrderCalculatorDialog(self)
        dialog.exec()