from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from models.material import MaterialRepository
from services.mrp_service import MRPService


class MRPView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        # Load UI designed in Qt Designer
        uic.loadUi("ui/MRPView.ui", self)
        
        # Connect buttons
        self.btn_calculate_mrp.clicked.connect(self.load_mrp_data)
        self.btn_search.clicked.connect(self.load_mrp_data)
        
        # Enable mouse tracking for proper tooltip display
        self.tableMRP.setMouseTracking(True)
        
        # --- Fill cb_material with all materials used in BOM ---
        self.cb_material.clear()
        self.cb_material.addItem("All", None)  # default option
        materials = MaterialRepository.get_all_materials()
        for mat in materials:
            self.cb_material.addItem(mat.name, mat.id)

        # --- Fill cb_priority with business priorities ---
        self.cb_priority.clear()
        self.cb_priority.addItem("All", None)
        self.cb_priority.addItem("Shortage", "shortage")
        self.cb_priority.addItem("OK", "ok")
        self.cb_priority.addItem("Surplus", "surplus")

        # --- Connect combo boxes to reload data on change ---
        self.cb_material.currentIndexChanged.connect(self.load_mrp_data)
        self.cb_priority.currentIndexChanged.connect(self.load_mrp_data)
        
    def load_view(self):
        # Emit info message when view is loaded
        self.statusMessage.emit("MRP Analysis loaded!", "info")
        
    def load_mrp_data(self):
        try:
            MAX_VISIBLE = 5  # max number of items to display in orders table cell

            # Call backend service to generate procurement plan
            result = MRPService.generate_procurement_plan()
            materials = result["all_materials"]

            # Clear table before inserting new data
            self.tableMRP.setRowCount(0)

            materials_to_order = {}  # Dict to track materials that need ordering
            orders_to_procure = set()  # Set of all orders to be procured
            earliest_deadline = None  # Track the earliest deadline

            # --- Filtering by search text ---
            search_text = self.leOrder.text().strip().lower() if hasattr(self, 'leOrder') else ""
            if search_text:
                materials = [
                    m for m in materials
                    if search_text in m.material_name.lower()
                ]
            self.statusMessage.emit(f"MRP data loaded ({len(materials)} items) for search '{search_text}'.", "success")

            # --- Filtering by selected material ---
            selected_material_id = self.cb_material.currentData()
            if selected_material_id:
                materials = [m for m in materials if getattr(m, "material_id", None) == selected_material_id]

            # --- Filtering by priority ---
            selected_priority = self.cb_priority.currentData()
            if selected_priority:
                if selected_priority == "shortage":
                    materials = [m for m in materials if (m.quantity_needed - m.quantity_in_stock) > 0]
                elif selected_priority == "surplus":
                    materials = [m for m in materials if (m.quantity_needed - m.quantity_in_stock) < 0]
                elif selected_priority == "ok":
                    materials = [m for m in materials if (m.quantity_needed - m.quantity_in_stock) == 0]

            # --- Check if any data is left after filtering ---
            if not materials:
                self.statusMessage.emit("No data found for selected filters.", "warning")
                self.lbl_pending_orders.setText("📋 Pending orders: 0")
                self.lbl_to_order.setText("No materials to order")
                self.lbl_to_order.setToolTip("")
                self.lbl_earliest_deadline.setText("⏰ Earliest deadline: N/A")
                return
            else:
                self.statusMessage.emit(f"MRP data loaded ({len(materials)} items).", "success")

            # --- Populate table rows ---
            for material in materials:
                row_position = self.tableMRP.rowCount()
                self.tableMRP.insertRow(row_position)

                # Material info columns
                self.tableMRP.setItem(row_position, 0, QTableWidgetItem(material.material_name))
                self.tableMRP.setItem(row_position, 1, QTableWidgetItem(material.unit))
                self.tableMRP.setItem(row_position, 2, QTableWidgetItem(f"{material.quantity_needed:.2f}"))
                self.tableMRP.setItem(row_position, 3, QTableWidgetItem(f"{material.quantity_in_stock:.2f}"))

                # Difference column (Shortage / Surplus / OK)
                difference = material.quantity_needed - material.quantity_in_stock
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
                    tooltip_text = "" # No tooltip if OK

                # Configure difference cell appearance and tooltip
                diff_item = QTableWidgetItem(text)
                diff_item.setBackground(QtGui.QBrush(bg_color))
                diff_item.setForeground(QtGui.QBrush(fg_color))
                diff_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                diff_item.setToolTip(tooltip_text)
                self.tableMRP.setItem(row_position, 4, diff_item)

                # Deadline column (single value from model)
                deadline_item = QTableWidgetItem(str(material.deadline) if material.deadline else "N/A")
                deadline_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.tableMRP.setItem(row_position, 5, deadline_item)

                # Update earliest deadline
                current_deadline = material.deadline
                if current_deadline and (earliest_deadline is None or current_deadline < earliest_deadline):
                    earliest_deadline = current_deadline

                # Orders requiring this material
                orders = material.orders_requiring if isinstance(material.orders_requiring, list) else ([material.orders_requiring] if material.orders_requiring else [])
                orders = [o for o in orders if o is not None]

                # Limit visible items and tooltip for extra
                orders_to_show = orders[:MAX_VISIBLE]
                orders_tooltip = orders[MAX_VISIBLE:]

                orders_item = QTableWidgetItem(", ".join(map(str, orders_to_show)))
                if orders_tooltip:
                    orders_item.setToolTip(", ".join(map(str, orders_tooltip)))
                self.tableMRP.setItem(row_position, 6, orders_item)

                # Collect all orders for summary label
                orders_to_procure.update(orders)

            # --- Update summary labels ---
            self.lbl_pending_orders.setText(f"📋 Pending orders: {len(orders_to_procure)}")

            if materials_to_order:
                to_order_text = ", ".join(f"{name}: {qty:.2f}" for name, qty in materials_to_order.items())
                self.lbl_to_order.setText(f"➕ To order: {to_order_text}")
            else:
                self.lbl_to_order.setText("No need to order new resources")

            # Tooltip for label with material status details
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

            # Earliest deadline label
            self.lbl_earliest_deadline.setText(f"⏰ Earliest deadline: {earliest_deadline}")

            # Emit success message
            self.statusMessage.emit("MRP calculation completed!", "success")

        except Exception as e:
            print(e)
            self.statusMessage.emit("Error while loading MRP data", "error")