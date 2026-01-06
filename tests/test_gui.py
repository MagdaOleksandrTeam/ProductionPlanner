import time
import pytest
from PyQt6 import QtCore, QtWidgets
from main_window import MainWindow
from models.database import init_db
from dialogs.dialog_views import MaterialDialog

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app(qtbot):
    init_db() 
    test_app = MainWindow()
    qtbot.addWidget(test_app)
    return test_app

def test_ft_01_add_material_logic(app, qtbot):
    #Test FT-01 dodawanie materiału
    # Zakładka materiałów
    qtbot.mouseClick(app.btn_material, QtCore.Qt.MouseButton.LeftButton)
    
    # Funkcja, która wypełni wyskakujące okno
    def handle_dialog():
        # Szuka aktywnego okna MaterialDialog
        all_widgets = QtWidgets.QApplication.topLevelWidgets()
        for widget in all_widgets:
            if isinstance(widget, MaterialDialog):
                # Wypełnia pola
                widget.leName.setText("Glass")
                widget.sbQuantity.setValue(100)
                # Akceptuje dialog
                widget.accept()
                return

    # Uruchamia nadzorcę okna z lekkim opóźnieniem
    QtCore.QTimer.singleShot(200, handle_dialog)
    
    # Klika przycisk dodawania, który otwiera okno
    qtbot.mouseClick(app.material_page.btn_addMaterial, QtCore.Qt.MouseButton.LeftButton)
    
    # Sprawdzenie wyniku w statusbarze
    assert "Material added successfully!" in app.statusbar.currentMessage()

def test_ft_02_validation_empty_fields(app, qtbot):
    """Test FT-02: Reakcja na brak danych w oknie dialogowym"""
    qtbot.mouseClick(app.btn_material, QtCore.Qt.MouseButton.LeftButton)
    
    def handle_empty_dialog():
        all_widgets = QtWidgets.QApplication.topLevelWidgets()
        for widget in all_widgets:
            if isinstance(widget, MaterialDialog):
                widget.leName.setText("") # Czyści pole
                widget.accept()
                return

    QtCore.QTimer.singleShot(200, handle_empty_dialog)
    qtbot.mouseClick(app.material_page.btn_addMaterial, QtCore.Qt.MouseButton.LeftButton)
    
    msg = app.statusbar.currentMessage()
    assert msg != ""
    
def test_ft_03_full_navigation(app, qtbot):
    """Test FT-03: Weryfikacja przełączania wszystkich widoków aplikacji"""
    
    # Mapowanie przycisków do stron
    nav_checks = [
        (app.btn_dashboard, app.dashboard_page),
        (app.btn_material, app.material_page),
        (app.btn_product, app.product_page),
        (app.btn_bom, app.bom_page),
        (app.btn_machine, app.machine_page),
        (app.btn_orders, app.orders_page),
        (app.btn_mrp, app.mrp_page),
        (app.btn_schedule, app.schedule_page),
        (app.btn_reports, app.reports_page)
    ]

    for btn, expected_page in nav_checks:
        # Klika przycisk
        qtbot.mouseClick(btn, QtCore.Qt.MouseButton.LeftButton)
        qtbot.wait(100) # Pauza na odświeżenie GUI
        
        # Sprawdza, czy obecnie widoczny widget w stackedWidget to ten oczekiwany
        current_widget = app.stackedWidget.currentWidget()
        assert current_widget == expected_page, f"Błąd: Przycisk {btn.objectName()} nie otworzył poprawnej strony!"

def test_ft_04_schedule_gantt_generation(app, qtbot):
    """Test FT-04: Generowanie planu na wykresie Gantta"""
    # Zakładka Schedule
    qtbot.mouseClick(app.btn_schedule, QtCore.Qt.MouseButton.LeftButton)
    qtbot.wait(200)
    
    # Czy widok jest aktywny
    assert app.stackedWidget.currentWidget() == app.schedule_page
    
    # Kliknięcie przycisku generowania planu
    qtbot.mouseClick(app.schedule_page.btnGenerateSchedule, QtCore.Qt.MouseButton.LeftButton)
    
    # Oczekiwanie na przeliczenie algorytmu i odświeżenie wykresu
    qtbot.wait(1200) 
    
    # Sprawdzenie, czy statusbar potwierdził operację
    msg = app.statusbar.currentMessage()
    assert msg != "" or "Success" in msg