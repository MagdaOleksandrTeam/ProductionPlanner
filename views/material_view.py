from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from models.material import MaterialRepository
from dialogs.dialog_views import MaterialDialog, ConfirmDialog

class MaterialView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        # load the UI from .ui file
        uic.loadUi("ui/MaterialView.ui", self)
        
        # Connect buttons to their functions
        self.btn_material_search.clicked.connect(self.search_items)
        self.btn_addMaterial.clicked.connect(self.add_material)
        self.btn_editMaterial.clicked.connect(self.edit_material)
        self.btn_deleteMaterial.clicked.connect(self.delete_material)

        self.load_materials()
        
    def load_view(self):
        self.statusMessage.emit("Material view loaded!", "info")
        
    # Loads all materials from db to the table
    def load_materials(self):
        self.tableMaterial.setRowCount(0)
        materials = MaterialRepository.get_all_materials()

        # Insert each material to the table
        for material in materials:
            row_position = self.tableMaterial.rowCount()
            self.tableMaterial.insertRow(row_position)
            self.tableMaterial.setItem(row_position, 0, QTableWidgetItem(str(material.id)))
            self.tableMaterial.setItem(row_position, 1, QTableWidgetItem(material.name))
            self.tableMaterial.setItem(row_position, 2, QTableWidgetItem(material.unit))
            self.tableMaterial.setItem(row_position, 3, QTableWidgetItem(str(material.quantity)))
            
            
    # Filters materials based on the search query, if there is no results - emits error
    def search_items(self):
        query = self.le_material.text().strip().lower()
        table = self.tableMaterial
        total_rows = table.rowCount()
        found_rows = []

        if total_rows == 0:
            self.statusMessage.emit("No data to search.", "error")
            return

        if not query:
            # If search field is empty, show all rows
            for row in range(total_rows):
                table.setRowHidden(row, False)
            self.statusMessage.emit("Filter cleared – showing all materials.", "info")
            return

        # Search through all rows
        for row in range(total_rows):
            item = table.item(row, 1) #by material name
            if item and query in item.text().lower():
                table.setRowHidden(row, False)
                found_rows.append(item.text())
            else:
                table.setRowHidden(row, True)

        if found_rows:
            msg = f"Found {len(found_rows)} material{'s' if len(found_rows) > 1 else ''} matching: '{query}'"
            self.statusMessage.emit(msg, "success")
        else:
            self.statusMessage.emit(f"No materials found matching query: '{query}'.", "error")
            
            
    # Adds new material to db via MaterialDialog
    def add_material(self):
        dialog = MaterialDialog()
        if dialog.exec():  # clicked save
            new_material = dialog.get_material()
            MaterialRepository.add_material(new_material)
            self.load_materials() # reload
            self.statusMessage.emit("Material added successfully!", "success")
        
        
    # Edits selected material, if no material selected - emit warning msg
    def edit_material(self):
        selected_rows = self.tableMaterial.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a material to edit!", "warning")
            return

        row = selected_rows[0].row()
        material_id = int(self.tableMaterial.item(row, 0).text())
        material = MaterialRepository.get_material_by_id(material_id)

        dialog = MaterialDialog(material)
        if dialog.exec():  # OK
            updated_material = dialog.get_material()
            updated_material.id = material.id
            MaterialRepository.update_material(updated_material)
            
            self.load_materials()
            self.statusMessage.emit("Material updated successfully!", "success")
        
        
    # Deletes material from db, if no material selected - emit warning msg  
    def delete_material(self):
        selected_rows = self.tableMaterial.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a material to delete!", "warning")
            return

        row = selected_rows[0].row()
        material_id = int(self.tableMaterial.item(row, 0).text())
        material = MaterialRepository.get_material_by_id(material_id)

        dialog = ConfirmDialog(f"Are you sure you want to delete material: '{material.name}'?")
        if dialog.exec():  # Yes
            MaterialRepository.delete_material(material)
            self.load_materials()
            self.statusMessage.emit("Material deleted successfully!", "success")