from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from models.material import Material

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


# MaterialView Delete
class ConfirmDialog(QDialog):
    def __init__(self, message: str):
        super().__init__()
        uic.loadUi("ui/ConfirmDialog.ui", self)
        self.lblMessage.setText(message)
        self.btn_confirm_dialog.accepted.connect(self.accept)
        self.btn_confirm_dialog.rejected.connect(self.reject)