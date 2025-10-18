from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from models.material import Material

# Material Dialog
class MaterialDialog(QDialog):
    def __init__(self, material: Material = None):
        super().__init__()
        uic.loadUi("ui/materialDialog.ui", self)

        if material:
            self.leName.setText(material.name)
            self.cbUnit.setCurrentText(material.unit)
            self.sbQuantity.setValue(material.quantity)
            self.teDescription.setPlainText(getattr(material, "description", ""))
        else:
            self.leName.setText("")
            self.cbUnit.setCurrentIndex(0)
            self.sbQuantity.setValue(0)
            self.teDescription.setPlainText("")

        self.MaterialButtonBox.accepted.connect(self.accept)
        self.MaterialButtonBox.rejected.connect(self.reject)

    def get_material(self) -> Material:
        return Material(
            id=0,
            name=self.leName.text(),
            unit=self.cbUnit.currentText(),
            quantity=self.sbQuantity.value()
        )


# Confirm Dialog
class ConfirmDialog(QDialog):
    def __init__(self, message: str):
        super().__init__()
        uic.loadUi("ui/ConfirmDialog.ui", self)
        self.labelMessage.setText(message)
        self.ConfirmButtonBox.accepted.connect(self.accept)
        self.ConfirmButtonBox.rejected.connect(self.reject)