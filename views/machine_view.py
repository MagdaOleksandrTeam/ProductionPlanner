from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from models.machine import MachineRepository, MachineRecipeRepository
from dialogs import ConfirmDialog, MachineDialog, MachineRecipeDialog

class MachineView(QWidget):
# Main view for managing production machines. 
# Shows all machines, allows add/edit/delete and managing machine-product recipes
    statusMessage = pyqtSignal(str, str)  # info, success, warning, error

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/MachineView.ui", self)

        # Connect buttons
        self.btn_addMachine.clicked.connect(self.add_machine)
        self.btn_editMachine.clicked.connect(self.edit_machine)
        self.btn_deleteMachine.clicked.connect(self.delete_machine)
        self.btn_search_machine.clicked.connect(self.search_items)

        # Table double-click opens recipe dialog
        self.tableMachines.itemDoubleClicked.connect(self.open_machine_recipes)

        # Load machines into table
        self.load_machines()

    def load_view(self):
        self.statusMessage.emit("Machine view loaded!", "info")

    def load_machines(self):
    # Load all machines into the table with recipe count
        self.tableMachines.setRowCount(0)
        machines = MachineRepository.get_all_machines()

        for machine in machines:
            row = self.tableMachines.rowCount()
            self.tableMachines.insertRow(row)
            self.tableMachines.setItem(row, 0, QTableWidgetItem(str(machine.id)))
            self.tableMachines.setItem(row, 1, QTableWidgetItem(machine.name))

            # Count recipes for this machine
            recipes = MachineRecipeRepository.get_recipes_by_machine_id(machine.id)
            self.tableMachines.setItem(row, 2, QTableWidgetItem(str(len(recipes))))


    # Filters machines based on the search query, if there is no results - emits error
    def search_items(self):
        query = self.le_machine.text().strip().lower()
        table = self.tableMachines
        total_rows = table.rowCount()
        found_rows = []

        if total_rows == 0:
            self.statusMessage.emit("No data to search.", "error")
            return

        if not query:
            # If search field is empty, show all rows
            for row in range(total_rows):
                table.setRowHidden(row, False)
            self.statusMessage.emit("Filter cleared – showing all machines.", "info")
            return

        # Search through all rows
        for row in range(total_rows):
            item = table.item(row, 1) #by machine name
            if item and query in item.text().lower():
                table.setRowHidden(row, False)
                found_rows.append(item.text())
            else:
                table.setRowHidden(row, True)

        if found_rows:
            msg = f"Found {len(found_rows)} machine{'s' if len(found_rows) > 1 else ''} matching: '{query}'"
            self.statusMessage.emit(msg, "success")
        else:
            self.statusMessage.emit(f"No machines found matching query: '{query}'.", "error")
    
    
    # CRUD operations for machines
    def add_machine(self):
        from dialogs import MachineDialog
        dialog = MachineDialog()
        if dialog.exec():
            new_machine = dialog.get_machine()
            MachineRepository.add_machine(new_machine)
            self.load_machines()
            self.statusMessage.emit("Machine added successfully!", "success")

    def edit_machine(self):
        selected_rows = self.tableMachines.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a machine to edit!", "warning")
            return

        row = selected_rows[0].row()
        machine_id = int(self.tableMachines.item(row, 0).text())
        machine = MachineRepository.get_machine_by_id(machine_id)


        dialog = MachineDialog(machine)
        if dialog.exec():
            updated_machine = dialog.get_machine()
            updated_machine.id = machine.id
            try:
                MachineRepository.update_machine(updated_machine)
                self.load_machines()
                self.statusMessage.emit("Machine updated successfully!", "success")
            except ValueError as e:
                self.statusMessage.emit(str(e), "error")

    def delete_machine(self):
        selected_rows = self.tableMachines.selectionModel().selectedRows()
        if not selected_rows:
            self.statusMessage.emit("Please select a machine to delete!", "warning")
            return

        row = selected_rows[0].row()
        machine_id = int(self.tableMachines.item(row, 0).text())
        machine = MachineRepository.get_machine_by_id(machine_id)

        dialog = ConfirmDialog(f"Are you sure you want to delete machine: '{machine.name}'?")
        if dialog.exec():
            MachineRepository.delete_machine(machine)
            self.load_machines()
            self.statusMessage.emit("Machine deleted successfully!", "success")


    # Open MachineRecipeDialog
    def open_machine_recipes(self, item):
        row = item.row()
        machine_id = int(self.tableMachines.item(row, 0).text())
        dialog = MachineRecipeDialog(machine_id)
        dialog.exec()
        # reload machine table to update recipe count
        self.load_machines()