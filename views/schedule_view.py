from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsRectItem

from services.scheduling_service import SchedulingService

class ScheduleView(QWidget):
    # Signal to send status msg (info, success, warning, error)
    statusMessage = pyqtSignal(str, str)
    def __init__(self, scheduling_service: SchedulingService):
        super().__init__()
        self.scheduling_service = scheduling_service
        uic.loadUi("ui/ScheduleView.ui", self)
        
        # Connect action buttons
        self.btnGenerateSchedule.clicked.connect(self.generate_plan)
        self.btnExportReport.clicked.connect(self.export_report)
        self.btnReload.clicked.connect(self.reload)
        
         # Initialize Gantt chart scene and link it to QGraphicsView
        self.scene = QGraphicsScene()
        self.graphicsGantt.setScene(self.scene) #connect scene to QGraphicsView
        
        # Store the currently loaded production plan
        self.current_plan = []
        
    def load_view(self):
        # Emit status message when view is loaded
        self.statusMessage.emit("Schedule (Gantt) loaded!", "info")
        
    def generate_plan(self):
        "Generates new production plan"
        self.statusMessage.emit("Generating production plan...", "info")
        self.current_plan = self.scheduling_service.generate_plan_from_scratch()
        
        if self.current_plan:
            self.statusMessage.emit(f"Plan generated: {len(self.current_plan)} orders scheduled", "success")
        else:
            self.statusMessage.emit("No orders to schedule", "warning")
            
        # Print current plan to console (for debugging)
        print("Current plan:", self.current_plan)
        
         # Temporary placeholder rectangle to verify QGraphicsView is working
        self.scene.clear()  # Clear the scene before drawing new items
        rect = QGraphicsRectItem(0, 0, 100, 40) # x, y, width, height
        rect.setBrush(QBrush(QColor("skyblue"))) # Fill color
        self.scene.addItem(rect)
        
    
    def reload(self):
        "Reloads the current production plan from the service."
        self.statusMessage.emit("Reloading current production plan...", "info")
        self.current_plan = self.scheduling_service.get_current_plan()
        
        if self.current_plan:
            self.statusMessage.emit(f"Plan reloaded: {len(self.current_plan)} orders", "success")
        else:
            self.statusMessage.emit("No plan found", "warning")
            
        # Print reloaded plan to console (for debugging)
        print("Reloaded plan:", self.current_plan)
        
        # TODO: Add actual Gantt chart rendering here
        
    def export_report(self):
        # Placeholder for export report functionality.
        print("Export clicked")
        