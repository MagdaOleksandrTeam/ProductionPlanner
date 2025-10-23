from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from models.material import MaterialRepository
from dialogs import MaterialDialog, ConfirmDialog

class MaterialView(QWidget):
    statusMessage = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/MaterialView.ui", self)

        self.btn_addMaterial.clicked.connect(self.add_material)
        self.btn_editMaterial.clicked.connect(self.edit_material)
        self.btn_deleteMaterial.clicked.connect(self.delete_material)

        self.load_materials()
        
    def load_view(self):
        self.statusMessage.emit("Material view loaded!", "info")
        
    def load_materials(self):
        self.tableMaterial.setRowCount(0)

        materials = MaterialRepository.get_all_materials()

        for material in materials:
            row_position = self.tableMaterial.rowCount()
            self.tableMaterial.insertRow(row_position)
            self.tableMaterial.setItem(row_position, 0, QTableWidgetItem(str(material.id)))
            self.tableMaterial.setItem(row_position, 1, QTableWidgetItem(material.name))
            self.tableMaterial.setItem(row_position, 2, QTableWidgetItem(material.unit))
            self.tableMaterial.setItem(row_position, 3, QTableWidgetItem(str(material.quantity)))
            
    def add_material(self):
        dialog = MaterialDialog()
        if dialog.exec():  # clicked save
            new_material = dialog.get_material()
            MaterialRepository.add_material(new_material)
            self.load_materials() #reload
            self.statusMessage.emit("Material added successfully!", "success")
        
    def edit_material(self):
        selected_rows = self.tableMaterial.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a material to edit!", "error")
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
        
    def delete_material(self):
        selected_rows = self.tableMaterial.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a material to delete!", "error")
            return

        row = selected_rows[0].row()
        material_id = int(self.tableMaterial.item(row, 0).text())
        material = MaterialRepository.get_material_by_id(material_id)

        dialog = ConfirmDialog(f"Are you sure you want to delete material: '{material.name}'?")
        if dialog.exec():  # Yes
            MaterialRepository.delete_material(material)
            self.load_materials()
            self.statusMessage.emit("Material deleted successfully!", "success")