from PyQt6 import uic
from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM, BOMRepository
from models.machine import Machine, MachineRecipe, MachineRepository, MachineRecipeRepository
from models.order import ProductionOrder

# ----------- MaterialView Add/Edit -------------
class MaterialDialog(QDialog):
    def __init__(self, material: Material = None):
        super().__init__()
        uic.loadUi("ui/materialDialog.ui", self)

        # Populate fields if editing an existing material
        if material:
            self.leName.setText(material.name)
            self.cbUnit.setCurrentText(material.unit)
            self.sbQuantity.setValue(material.quantity)
        else:
            self.leName.setText("")
            self.cbUnit.setCurrentIndex(0)
            self.sbQuantity.setValue(0)

        # Connect dialog buttons to accept/reject
        self.MaterialButtonBox.accepted.connect(self.accept)
        self.MaterialButtonBox.rejected.connect(self.reject)


    # Return a Material object with entered values.
    def get_material(self) -> Material:
        return Material(
            id=0,
            name=self.leName.text(),
            unit=self.cbUnit.currentText(),
            quantity=self.sbQuantity.value()
        )

# ------------- ProductView Add/Edit --------------
class ProductDialog(QDialog):
    def __init__(self, product: Product = None):
        super().__init__()
        uic.loadUi("ui/ProductDialog.ui", self)

        # Populate fields if editing existing product
        if product:
            self.leName.setText(product.name)
            self.sbQuantity.setValue(product.quantity)
            self.cbUnit.setCurrentText(product.unit)
            self.leDescription.setText(product.description)
            
        else:
            self.leName.setText("")
            self.sbQuantity.setValue(0)
            self.cbUnit.setCurrentIndex(0)
            self.leDescription.setText("")
            
        # Connect dialog buttons to accept/reject
        self.ProductButtonBox.accepted.connect(self.accept)
        self.ProductButtonBox.rejected.connect(self.reject)
        
    def get_product(self) -> Product:
        # Return a Product object with entered values.
        return Product(
                id=0,
                name=self.leName.text(),
                quantity=self.sbQuantity.value(),
                unit=self.cbUnit.currentText(),
                description=self.leDescription.text()
                )
        

# ------------- BOM Add/Edit ----------------
class BOMDialog(QDialog):
# Dialog for adding or editing a BOM entry (product-material relationship).
    def __init__(self, bom: BOM = None):
        super().__init__()
        uic.loadUi("ui/BOMDialog.ui", self)

        # Load all products and materials into cb
        self.cbProduct.clear()
        self.cbMaterial.clear()
        products = ProductRepository.get_all_products()
        materials = MaterialRepository.get_all_materials()

        for p in products:
            self.cbProduct.addItem(f"{p.id}. {p.name}", p.id)
        for m in materials:
            self.cbMaterial.addItem(f"{m.id}. {m.name}", m.id)

        # Populate fields if editing an existing BOM
        if bom:
            # set product
            index_product = self.cbProduct.findData(bom.product_id)
            if index_product != -1:
                self.cbProduct.setCurrentIndex(index_product)
            # set material
            index_material = self.cbMaterial.findData(bom.material_id)
            if index_material != -1:
                self.cbMaterial.setCurrentIndex(index_material)
            self.sbQuantity.setValue(bom.quantity_needed)
        else:
            self.sbQuantity.setValue(0)

        # Connect dialog buttons to accept/reject
        self.BOMButtonBox.accepted.connect(self.accept)
        self.BOMButtonBox.rejected.connect(self.reject)

    # Return a BOM object with selected product, material, and quantity.
    def get_bom(self) -> BOM:
        product_id = self.cbProduct.currentData()
        material_id = self.cbMaterial.currentData()
        return BOM(
            id=0,
            product_id=product_id,
            material_id=material_id,
            quantity_needed=self.sbQuantity.value()
        )

# ------------ Machine Add/Edit ------------
# Dialog for adding or editing a Machine.
class MachineDialog(QDialog):
    def __init__(self, machine: Machine = None):
        super().__init__()
        uic.loadUi("ui/MachineDialog.ui", self)

        if machine:
            self.leName.setText(machine.name)
        else:
            self.leName.setText("")

        # Connect OK/Cancel buttons
        self.MachineButtonBox.accepted.connect(self.accept)
        self.MachineButtonBox.rejected.connect(self.reject)

    def get_machine(self) -> Machine:
        """Return a Machine object with entered values."""
        return Machine(
            id=0,  # Will be set when added to DB or edited
            name=self.leName.text()
        )

# ------------- Machine Recipe Add/Edit ----------------
class MachineRecipeDialog(QDialog):
#Dialog for viewing, adding, editing and deleting Machine-Product recipes.
#Shows which products a machine can produce and their capacities.
    def __init__(self, machine_id: int):
        super().__init__()
        uic.loadUi("ui/MachineRecipeDialog.ui", self)
        self.machine_id = machine_id
        # Load machine name dynamically
        machine = MachineRepository.get_machine_by_id(machine_id)
        if machine:
            self.lbl_name.setText(f"Recipes for machine: {machine.name}")
        else:
            self.lbl_name.setText("Recipes for machine: (unknown)")

        # Connect buttons
        self.btn_addRecipe.clicked.connect(self.add_recipe)
        self.btn_editRecipe.clicked.connect(self.edit_recipe)
        self.btn_deleteRecipe.clicked.connect(self.delete_recipe)

        # Load recipes into table
        self.load_recipes()

    def load_recipes(self):
    # Load all recipes for selected machine into the table.
        self.tableRecipes.setRowCount(0)
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(self.machine_id)

        for r in recipes:
            row = self.tableRecipes.rowCount()
            self.tableRecipes.insertRow(row)

            # get product name
            product = ProductRepository.get_product_by_id(r.product_id)
            product_name = product.name if product else f"#{r.product_id}"

            self.tableRecipes.setItem(row, 0, QTableWidgetItem(str(r.id)))
            self.tableRecipes.setItem(row, 1, QTableWidgetItem(product_name))
            self.tableRecipes.setItem(row, 2, QTableWidgetItem(str(r.production_capacity)))

    # Add recipe
    def add_recipe(self):
        # Open dialog to add a new recipe.
        dialog = RecipeAddEditDialog()
        if dialog.exec():
            new_recipe = dialog.get_recipe()
            new_recipe.machine_id = self.machine_id
            MachineRecipeRepository.add_machine_recipe(new_recipe)
            self.load_recipes()

    # Edit recipe
    def edit_recipe(self):
        # Open dialog to edit selected recipe
        selected_rows = self.tableRecipes.selectionModel().selectedRows()
        if not selected_rows:
            return  # no row selection

        row = selected_rows[0].row()
        recipe_id = int(self.tableRecipes.item(row, 0).text())
        recipe = MachineRecipeRepository.get_machine_recipe_by_id(recipe_id)

        dialog = RecipeAddEditDialog(recipe)
        if dialog.exec():
            updated_recipe = dialog.get_recipe()
            updated_recipe.id = recipe.id
            updated_recipe.machine_id = recipe.machine_id
            MachineRecipeRepository.update_machine_recipe(updated_recipe)
            self.load_recipes()

    # Delete recipe
    def delete_recipe(self):
        # Delete selected recipe after confirmation
        selected_rows = self.tableRecipes.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        recipe_id = int(self.tableRecipes.item(row, 0).text())
        recipe = MachineRecipeRepository.get_machine_recipe_by_id(recipe_id)

        dialog = ConfirmDialog(f"Are you sure you want to delete this recipe (ID {recipe.id})?")
        if dialog.exec():
            MachineRecipeRepository.delete_machine_recipe(recipe)
            self.load_recipes()
    
# ----------- Recipe Add/Edit ---------------
class RecipeAddEditDialog(QDialog):
# Dialog for adding/editing Recipe. Allows selecting a product and capacity.
    def __init__(self, recipe: MachineRecipe = None):
        super().__init__()
        uic.loadUi("ui/RecipeAddEditDialog.ui", self)

        # Load all products into cb
        self.cb_product.clear()
        products = ProductRepository.get_all_products()
        for p in products:
            self.cb_product.addItem(f"{p.id}. {p.name}", p.id)

        # Populate fields if editing an existing recipe
        if recipe:
            index = self.cb_product.findData(recipe.product_id)
            if index != -1:
                self.cb_product.setCurrentIndex(index)
            self.sb_capacity.setValue(recipe.production_capacity)
        else:
            self.sb_capacity.setValue(0)

        # Connect buttons to accept/reject
        self.RecipebuttonBox.accepted.connect(self.accept)
        self.RecipebuttonBox.rejected.connect(self.reject)

    def get_recipe(self) -> MachineRecipe:
    # Return a MachineRecipe object with entered values
        return MachineRecipe(
            id=0,  # ID will be assigned when added to DB
            machine_id=0,  # This will be set in MachineView
            product_id=self.cb_product.currentData(),
            production_capacity=self.sb_capacity.value()
        )
        
# --------------- Order Add/Edit ------------------
class OrderDialog(QDialog):
# Dialog for adding/editing orders
    def __init__(self, order: ProductionOrder = None):
        super().__init__()
        uic.loadUi("ui/OrderDialog.ui", self)
        
        
        # Load products and machines
        self.cb_product.clear()
        self.cb_machine.clear()
        self.cb_status.clear()
        self.cb_priority.clear()
        
        products = ProductRepository.get_all_products()
        machines = MachineRepository.get_all_machines()
        
        for p in products:
            self.cb_product.addItem(f"{p.id}. {p.name}", p.id)
            
        for m in machines:
            self.cb_machine.addItem(f"{m.id}. {m.name}", m.id)
        
        statuses = ["in_queue", "in_progress", "completed"]
        priorities = ["1", "2", "3"]
        
        self.cb_status.addItems(statuses)
        self.cb_priority.addItems(priorities)
        
        # Populate fields if editing an existing order
        if order:
            # product
            index_product = self.cb_product.findData(order.product_id)
            if index_product != -1:
                self.cb_product.setCurrentIndex(index_product)

            # machine
            index_machine = self.cb_machine.findData(order.assigned_machine_id)
            if index_machine != -1:
                self.cb_machine.setCurrentIndex(index_machine)

            # quantity
            self.sb_quantity.setValue(order.quantity)

            # deadline
            if order.deadline:
                self.de_deadline.setDate(QDate.fromString(order.deadline, "yyyy-MM-dd"))

            # status and priority
            index_status = self.cb_status.findText(order.status)
            if index_status != -1:
                self.cb_status.setCurrentIndex(index_status)

            # priority – musi być int 1–3, więc szukamy po tekście (np. "1", "2", "3")
            index_priority = self.cb_priority.findText(str(order.priority))
            if index_priority != -1:
                self.cb_priority.setCurrentIndex(index_priority)

        else:
            # --- Add new order ---
            self.sb_quantity.setValue(1)
            self.de_deadline.setDate(QDate.currentDate())
            self.cb_status.setCurrentIndex(0)
            self.cb_priority.setCurrentIndex(1)

        # Connect dialog buttons to accept/reject
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    # Return Order with entered values
    def get_order(self) -> ProductionOrder:
        product_id = self.cb_product.currentData()
        assigned_machine_id = self.cb_machine.currentData()
        deadline_str = self.de_deadline.date().toString("yyyy-MM-dd")

        return ProductionOrder(
            id=0,
            product_id=product_id,
            quantity=self.sb_quantity.value(),
            deadline=deadline_str,
            assigned_machine_id=assigned_machine_id,
            status=self.cb_status.currentText(),
            priority=int(self.cb_priority.currentText())
        )
        
        
# ------------- Order Details Dialog ---------------
class OrderDetailsDialog(QDialog):
# Dialog with order details such as assigned machine and material required
    def __init__(self, order: ProductionOrder):
        super().__init__()
        uic.loadUi("ui/OrderDetailsDialog.ui", self)

        self.val_order_id.setText(str(order.id))
        self.val_product.setText(ProductRepository.get_product_by_id(order.product_id).name)
        self.val_quantity.setText(str(order.quantity))
        self.val_deadline.setText(order.deadline)
        self.val_priority.setText(str(order.priority))
        self.val_status.setText(order.status)
        self.val_assigned_machine.setText(
            MachineRepository.get_machine_by_id(order.assigned_machine_id).name
            if order.assigned_machine_id else "-"
        )
        self.val_created_date.setText(getattr(order, "created_date", "-"))

        # Calculate required materials
        bom_items = BOMRepository.get_bom_by_product_id(order.product_id)
        self.tableMaterials.setRowCount(len(bom_items))

        for row, bom in enumerate(bom_items):
            material = MaterialRepository.get_material_by_id(bom.material_id)
            if not material:
                continue

            # Calculating materials
            required_qty = bom.quantity_needed * order.quantity

            self.tableMaterials.setItem(row, 0, QTableWidgetItem(material.name))
            self.tableMaterials.setItem(row, 1, QTableWidgetItem(str(required_qty)))
            self.tableMaterials.setItem(row, 2, QTableWidgetItem(material.unit))

        self.tableMaterials.resizeColumnsToContents()

        # button close
        self.buttonBox.rejected.connect(self.reject)
            

# --------------- Delete Dialog ------------------
class ConfirmDialog(QDialog):
# Confirmation dialog for delete actions
    def __init__(self, message: str):
        super().__init__()
        uic.loadUi("ui/ConfirmDialog.ui", self)
        self.lblMessage.setText(message)
        self.btn_confirm_dialog.accepted.connect(self.accept)
        self.btn_confirm_dialog.rejected.connect(self.reject)
        
        
        
#calculator ststuses        
#self.show_local_status("No recipe data available for this product.", "warning")

#self.show_local_status("Estimation completed successfully!", "success")