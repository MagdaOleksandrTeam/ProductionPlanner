from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from services.mrp_service import MRPService

class MRPView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        # Load UI designed in Qt Designer
        uic.loadUi("ui/MRPView.ui", self)
        
        # Connect buttons
        #self.btn_mrp_search.clicked.connect(self.search_items)
        self.btn_calculate_mrp.clicked.connect(self.load_mrp_data)
        
    def load_view(self):
        # Emit info message when view is loaded
        self.statusMessage.emit("MRP Analysis loaded!", "info")
        
    def load_mrp_data(self):
        try:
            # Call backend service to generate procurement plan
            result = MRPService.generate_procurement_plan()
            materials = result["all_materials"]

            # Clear table before inserting new data
            self.tableMRP.setRowCount(0)

            materials_to_order = {} # Dict to track materials that need ordering
            orders_to_procure = set() # Set of all orders to be procured
            earliest_deadline = None # Track the earliest deadline

            for material in materials:
                row_position = self.tableMRP.rowCount()
                self.tableMRP.insertRow(row_position)
                # Fill table columns with material info
                self.tableMRP.setItem(row_position, 0, QTableWidgetItem(material.material_name))
                self.tableMRP.setItem(row_position, 1, QTableWidgetItem(material.unit))
                self.tableMRP.setItem(row_position, 2, QTableWidgetItem(f"{material.quantity_needed:.2f}"))
                self.tableMRP.setItem(row_position, 3, QTableWidgetItem(f"{material.quantity_in_stock:.2f}"))

                difference = material.quantity_needed - material.quantity_in_stock

                # === Difference column (Shortage / Surplus / OK) ===
                if difference > 0:
                    text = "Shortage"
                    bg_color = QtGui.QColor("#e74c3c")
                    fg_color = QtGui.QColor("#ffffff")
                    tooltip_text = f"Shortage: {difference:.2f}"
                    materials_to_order[material.material_name] = difference
                elif difference < 0:
                    text = "Surplus"
                    bg_color = QtGui.QColor("#27ae60")
                    fg_color = QtGui.QColor("#ffffff")
                    tooltip_text = f"Surplus: {abs(difference):.2f}"
                else:
                    text = "OK"
                    bg_color = QtGui.QColor("#bdc3c7")
                    fg_color = QtGui.QColor("#000000")
                    tooltip_text = ""  # No tooltip if OK

                # Configure difference cell appearance and tooltip
                diff_item = QTableWidgetItem(text)
                diff_item.setBackground(QtGui.QBrush(bg_color))
                diff_item.setForeground(QtGui.QBrush(fg_color))
                diff_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                diff_item.setToolTip(tooltip_text)
                self.tableMRP.setItem(row_position, 4, diff_item)

                # Set deadline and orders requiring this material
                self.tableMRP.setItem(row_position, 5, QTableWidgetItem(material.deadline))
                self.tableMRP.setItem(row_position, 6, QTableWidgetItem(", ".join(map(str, material.orders_requiring))))

                # Update earliest deadline
                if earliest_deadline is None or material.deadline < earliest_deadline:
                    earliest_deadline = material.deadline

                # Collect all orders for summary label
                orders_to_procure.update(material.orders_requiring)

            # --- Update summary labels ---
            self.lbl_pending_orders.setText(f"📋 Pending orders: {len(orders_to_procure)}")

            if materials_to_order:
                to_order_text = ", ".join(f"{name}: {qty:.2f}" for name, qty in materials_to_order.items())
                self.lbl_to_order.setText(f"➕ To order: {to_order_text}")
            else:
                self.lbl_to_order.setText("No need to order new resources")

            # Create tooltip for label with detailed material statuses
            all_tooltips = []
            for mat in materials:
                diff = mat.quantity_needed - mat.quantity_in_stock
                if diff > 0:
                    all_tooltips.append(f"{mat.material_name}: Shortage {diff:.2f}")
                elif diff < 0:
                    all_tooltips.append(f"{mat.material_name}: Surplus {abs(diff):.2f}")
                else:
                    all_tooltips.append(f"{mat.material_name}: OK")
            self.lbl_to_order.setToolTip("\n".join(all_tooltips))

            # earliest deadline
            self.lbl_earliest_deadline.setText(f"⏰ Earliest deadline: {earliest_deadline}")

            # Emit success message
            self.statusMessage.emit("MRP calculation completed!", "success")

        except Exception as e:
            print(e)
            self.statusMessage.emit("Error while loading MRP data", "error")