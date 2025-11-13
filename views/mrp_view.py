from PyQt6 import uic, QtGui, QtCore

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
#from services.mrp_service import MaterialRequirement
from services.mrp_service import MRPService

class MRPView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/MRPView.ui", self)
        
        #self.btn_mrp_search.clicked.connect(self.search_items)
        self.btn_calculate_mrp.clicked.connect(self.load_mrp_data)
        
    def load_view(self):
        self.statusMessage.emit("MRP Analysis loaded!", "info")
        
    def load_mrp_data(self):
        try:
            result = MRPService.generate_procurement_plan()
            materials = result["all_materials"]
            
            self.tableMRP.setRowCount(0)


        # Insert each material to the table
            for material in materials:
                row_position = self.tableMRP.rowCount()
                self.tableMRP.insertRow(row_position)
                
                self.tableMRP.setItem(row_position, 0, QTableWidgetItem(material.material_name))
                self.tableMRP.setItem(row_position, 1, QTableWidgetItem(material.unit))
                self.tableMRP.setItem(row_position, 2, QTableWidgetItem(f"{material.quantity_needed:.2f}"))
                self.tableMRP.setItem(row_position, 3, QTableWidgetItem(f"{material.quantity_in_stock:.2f}"))

                # === Difference column (color-coded) ===
                diff_value = material.quantity_difference
                diff_item = QTableWidgetItem(f"{diff_value:.2f}")
                diff_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                # Color by value
                if diff_value > 0:
                    # Shortage → red
                    bg_color = QtGui.QColor("#e74c3c")
                    fg_color = QtGui.QColor("#ffffff")
                elif diff_value < 0:
                    # Surplus → green
                    bg_color = QtGui.QColor("#27ae60")
                    fg_color = QtGui.QColor("#ffffff")
                else:
                    # neutral - grey
                    bg_color = QtGui.QColor("#bdc3c7")
                    fg_color = QtGui.QColor("#000000")

                diff_item.setBackground(QtGui.QBrush(bg_color))
                diff_item.setForeground(QtGui.QBrush(fg_color))
                diff_item.setToolTip(
                    "Positive = shortage (needs ordering)\nNegative = surplus (enough in stock)"
                )

                self.tableMRP.setItem(row_position, 4, diff_item)

                self.tableMRP.setItem(row_position, 5, QTableWidgetItem(material.deadline))
                self.tableMRP.setItem(row_position, 6, QTableWidgetItem(", ".join(map(str, material.orders_requiring))))
                self.statusMessage.emit("MRP calculation completed!", "success")
            
        except:
            self.statusMessage.emit("Error while loading MRP data", "error")