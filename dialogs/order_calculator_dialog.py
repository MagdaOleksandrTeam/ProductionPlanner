from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

from models.product import ProductRepository
from models.machine import MachineRepository, MachineRecipeRepository


class OrderCalculatorDialog(QDialog):
# Dialog for calculating production time of an order
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/OrderCalculatorDialog.ui", self)

        # --- Load all products and machines ---
        self.products = ProductRepository.get_all_products()
        self.machines = MachineRepository.get_all_machines()

        self.load_product_cb()  # Fill product combo
        self.load_machine_cb()  # Fill machine combo
        
        self.show_local_status("Order calculator ready!", "info")

        # --- Connect signals ---
        self.cb_product.currentIndexChanged.connect(self.on_product_changed)
        self.cb_machine.currentIndexChanged.connect(self.on_machine_changed)
        self.sb_quantity.valueChanged.connect(self.reset_local_status)  # reset status when quantity changes
        self.btn_calculate.clicked.connect(self.update_estimation)

        self.selected_capacity = None
        self.update_capacity_label()

    # --- ComboBox Loading ---
    def load_product_cb(self, filter_machine_id=None):
    #Load products into combo box. If a machine is selected, show only products that it can produce
        self.cb_product.blockSignals(True)  # temporarily block signals to avoid unwanted callbacks
        self.cb_product.clear()

        filtered_products = self.products
        if filter_machine_id is not None:
        # Keep only products that this machine can produce
            recipes = MachineRecipeRepository.get_recipes_by_machine_id(filter_machine_id)
            product_ids = [r.product_id for r in recipes]
            filtered_products = [p for p in self.products if p.id in product_ids]

        for p in filtered_products:
            self.cb_product.addItem(p.name, p.id)

        self.cb_product.blockSignals(False)

    def load_machine_cb(self, filter_product_id=None):
    # Load machines into combo box. 
    # If a product is selected, show only machines that can produce it.
        self.cb_machine.blockSignals(True)
        self.cb_machine.clear()

        filtered_machines = self.machines
        if filter_product_id is not None:
            recipes = MachineRecipeRepository.get_recipes_by_product_id(filter_product_id)
            machine_ids = [r.machine_id for r in recipes]
            filtered_machines = [m for m in self.machines if m.id in machine_ids]

        for m in filtered_machines:
            self.cb_machine.addItem(m.name, m.id)

        self.cb_machine.blockSignals(False)

    # --- ComboBox Change Handlers ---
    def on_product_changed(self):
    #When the product changes, update machines and reset status
        self.reset_local_status()
        product_id = self.cb_product.currentData()
        if product_id:
            self.load_machine_cb(filter_product_id=product_id)
        self.update_capacity_label()

    def on_machine_changed(self):
    #When the machine changes, update products and reset status
        self.reset_local_status()
        machine_id = self.cb_machine.currentData()
        if machine_id:
            self.load_product_cb(filter_machine_id=machine_id)
        self.update_capacity_label()

    # --- Capacity & Estimation ---
    def update_capacity_label(self):
    # Update the label showing machine capacity for the selected product
        machine_id = self.cb_machine.currentData()
        product_id = self.cb_product.currentData()

        if not machine_id or not product_id:
            self.lbl_capacity.setText("[---]")
            self.selected_capacity = None
            return

        # Find recipe that matches both selected machine and product
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(machine_id)
        recipe = next((r for r in recipes if r.product_id == product_id), None)

        if recipe:
            self.selected_capacity = recipe.production_capacity
            self.lbl_capacity.setText(f"{recipe.production_capacity} units/hour")
        else:
            self.selected_capacity = None
            self.lbl_capacity.setText("[no data]")

    def update_estimation(self):
    #Calculate estimated time after clicking btn "calculate"
        if not self.selected_capacity:
            self.show_local_status("No valid capacity available.", "error")
            return

        qty = self.sb_quantity.value()
        time_hours = qty / self.selected_capacity
        time_minutes = time_hours * 60
        self.show_local_status(
            f"Estimated production time: {time_hours:.2f} h ({time_minutes:.0f} minutes)", "success"
        )

    # --- Local Status Management ---
    def show_local_status(self, message: str, status: str = "info"):
    #Show a message in the local status label
        self.lblLocalStatus.setProperty("status", status)
        self.lblLocalStatus.setText(message)
        self.lblLocalStatus.style().unpolish(self.lblLocalStatus)
        self.lblLocalStatus.style().polish(self.lblLocalStatus)

    def reset_local_status(self):
    #Clear the status label when user changes selections or quantity
        self.lblLocalStatus.setProperty("status", "info")
        self.lblLocalStatus.setText("")
        self.lblLocalStatus.style().unpolish(self.lblLocalStatus)
        self.lblLocalStatus.style().polish(self.lblLocalStatus)