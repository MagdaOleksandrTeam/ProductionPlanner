from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM

#MaterialView Add/Edit
class MaterialDialog(QDialog):
    def __init__(self, material: Material = None):
        super().__init__()
        uic.loadUi("ui/materialDialog.ui", self)

        if material:
            self.leName.setText(material.name)
            self.cbUnit.setCurrentText(material.unit)
            self.sbQuantity.setValue(material.quantity)
        else:
            self.leName.setText("")
            self.cbUnit.setCurrentIndex(0)
            self.sbQuantity.setValue(0)

        self.MaterialButtonBox.accepted.connect(self.accept)
        self.MaterialButtonBox.rejected.connect(self.reject)

    def get_material(self) -> Material:
        return Material(
            id=0,
            name=self.leName.text(),
            unit=self.cbUnit.currentText(),
            quantity=self.sbQuantity.value()
        )

#ProductView Add/Edit
class ProductDialog(QDialog):
    def __init__(self, product: Product = None):
        super().__init__()
        uic.loadUi("ui/ProductDialog.ui", self)

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
            

        self.ProductButtonBox.accepted.connect(self.accept)
        self.ProductButtonBox.rejected.connect(self.reject)
        
    def get_product(self) -> Product:
        return Product(
                id=0,
                name=self.leName.text(),
                quantity=self.sbQuantity.value(),
                unit=self.cbUnit.currentText(),
                description=self.leDescription.text()
                )
        
#BOM Add/Edit
# -------------------- BOM DIALOG --------------------
class BOMDialog(QDialog):
    def __init__(self, bom: BOM = None):
        super().__init__()
        uic.loadUi("ui/BOMDialog.ui", self)

        # Załaduj wszystkie produkty i materiały do comboboxów
        self.cbProduct.clear()
        self.cbMaterial.clear()
        products = ProductRepository.get_all_products()
        materials = MaterialRepository.get_all_materials()

        for p in products:
            self.cbProduct.addItem(f"{p.id}. {p.name}", p.id)
        for m in materials:
            self.cbMaterial.addItem(f"{m.id}. {m.name}", m.id)

        # Jeśli edycja istniejącego BOM
        if bom:
            # ustaw wybrany produkt
            index_product = self.cbProduct.findData(bom.product_id)
            if index_product != -1:
                self.cbProduct.setCurrentIndex(index_product)
            # ustaw wybrany materiał
            index_material = self.cbMaterial.findData(bom.material_id)
            if index_material != -1:
                self.cbMaterial.setCurrentIndex(index_material)
            self.sbQuantity.setValue(bom.quantity_needed)
        else:
            self.sbQuantity.setValue(0)

        self.BOMButtonBox.accepted.connect(self.accept)
        self.BOMButtonBox.rejected.connect(self.reject)

    def get_bom(self) -> BOM:
        product_id = self.cbProduct.currentData()
        material_id = self.cbMaterial.currentData()
        return BOM(
            id=0,
            product_id=product_id,
            material_id=material_id,
            quantity_needed=self.sbQuantity.value()
        )

# Delete Dialog
class ConfirmDialog(QDialog):
    def __init__(self, message: str):
        super().__init__()
        uic.loadUi("ui/ConfirmDialog.ui", self)
        self.lblMessage.setText(message)
        self.btn_confirm_dialog.accepted.connect(self.accept)
        self.btn_confirm_dialog.rejected.connect(self.reject)
        
