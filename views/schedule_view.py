from PyQt6 import uic
from datetime import datetime, timedelta
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsRectItem

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates

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
        self.btnUpdate.clicked.connect(self.update_plan)
        self.btnReload.clicked.connect(self.reload)
        self.btnExportReport.clicked.connect(self.export_report)
        
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
        # Emit status instantly
        self.statusMessage.emit("Generating production plan...", "info")
        QApplication.processEvents()  # Force GUI to update immediately

        self.current_plan = self.scheduling_service.generate_plan_from_scratch()
        
        if self.current_plan:
            self.statusMessage.emit(f"Plan generated successfully: {len(self.current_plan)} orders scheduled", "success")
        else:
            self.statusMessage.emit("No orders to schedule", "warning")
            
        # Print to console (for debugging)
        print("Current plan:", self.current_plan)
        
        # Draw Gantt chart in the view
        self.render_gantt()
        
        self.statusMessage.emit("Done", "success")
        
        
    def update_plan(self):
        """Updates existing production plan with new orders"""
        self.statusMessage.emit("Updating plan...", "info")
        updated_plan = self.scheduling_service.update_plan_with_new_orders()
        
        if updated_plan:
            self.statusMessage.emit(f"Plan updated successfully: {len(updated_plan)} orders scheduled", "success")
        else:
            self.statusMessage.emit("No new orders to schedule", "warning")
        
        print("Updated plan:", updated_plan)
        self.render_gantt()
    
    def render_gantt(self):
        """Draws a simple Gantt chart for all machines based on self.current_plan."""

        # Clear previous scene
        self.scene.clear()
        if not self.current_plan:
            return

        # Configuration
        row_height = 40           # Height of each machine row
        machine_gap = 50          # Vertical gap between machines
        px_per_hour = 40          # Pixels per hour on the timeline
        time_step_hours = 1       # Time axis step (can increase to 2 for shorter chart)

        # Parse start and end times
        parsed = []
        for plan in self.current_plan:
            start = datetime.strptime(plan.planned_start_time, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(plan.planned_end_time, "%Y-%m-%d %H:%M:%S")
            parsed.append((plan, start, end))

        # Determine earliest start time for zero point
        start_zero = min(start for (_, start, _) in parsed)
        max_end = max(end for (_, _, end) in parsed)

        #Group plans by machine
        machines_plans = {}
        for plan, start, end in parsed:
            machines_plans.setdefault(plan.machine_id, []).append((plan, start, end))

        # Get dynamic machine list from DB
        from models.machine import MachineRepository
        all_machines = MachineRepository.get_all_machines()  # returns list of Machine objects with id and name

        # Status color mapping
        status_colors = {
            "planned": "lightblue",
            "in_progress": "lightgreen",
            "completed": "lightgray"
        }

        # Draw Gantt rows for all machines, even if no plans exist
        y_offset = 40

        for machine in all_machines:
            machine_id = machine.id
            machine_name = machine.name

            # Draw machine label
            label = self.scene.addText(machine_name)
            label.setPos(0, y_offset - 30)
            font = label.font()
            font.setBold(True)
            label.setFont(font)

            # Get plans for this machine, if any
            plans = machines_plans.get(machine_id, [])
            for plan, start, end in plans:
                duration_hours = (end - start).total_seconds() / 3600
                x = (start - start_zero).total_seconds() / 3600 * px_per_hour
                width = duration_hours * px_per_hour

                # Draw plan rectangle
                color = status_colors.get(plan.status, "skyblue")
                rect = QGraphicsRectItem(x, y_offset, width, row_height)
                rect.setBrush(QBrush(QColor(color)))
                rect.setToolTip(f"Order {plan.order_id}\nStatus: {plan.status}")
                self.scene.addItem(rect)

                # Draw order ID on rectangle
                text = self.scene.addText(str(plan.order_id))
                text.setPos(x + 5, y_offset + 5)

            # Move down for next machine
            y_offset += row_height + machine_gap

        # Draw time axis at top (hours)
        axis_y = 0
        total_hours = int((max_end - start_zero).total_seconds() / 3600)
        self.scene.addLine(0, axis_y, (total_hours + 2) * px_per_hour, axis_y)
        for h in range(0, total_hours + 1, time_step_hours):
            x = h * px_per_hour
            self.scene.addLine(x, axis_y - 5, x, axis_y + 5)
            label = (start_zero + timedelta(hours=h)).strftime("%H:%M")
            t = self.scene.addText(label)
            t.setPos(x - 15, axis_y - 20)

        # Draw day axis at bottom
        day_axis_y = y_offset + 10
        total_days = (max_end.date() - start_zero.date()).days + 1
        for d in range(total_days):
            day_start = start_zero + timedelta(days=d)
            x = (day_start - start_zero).total_seconds() / 3600 * px_per_hour
            self.scene.addLine(x, day_axis_y, x, day_axis_y + 5)
            label = day_start.strftime("%Y-%m-%d")
            text_item = self.scene.addText(label)
            text_item.setPos(x - 15, day_axis_y + 5)
    
    def reload(self):
        "Reloads the current production plan from the service."
        self.statusMessage.emit("Reloading plan...", "info")
        self.current_plan = self.scheduling_service.get_current_plan()
        
        if self.current_plan:
            self.statusMessage.emit(f"Plan reloaded: {len(self.current_plan)} orders", "success")
        else:
            self.statusMessage.emit("No plan found", "warning")
            
        print("Reloaded plan:", self.current_plan)
        self.render_gantt()
        self.statusMessage.emit("Done", "success")
        
        
    def export_report(self):
        """Export the current plan to a PDF Gantt chart"""
        if not self.current_plan:
            self.statusMessage.emit("No plan to export", "warning")
            return

        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not filename:
            return

        # load machine names
        from models.machine import MachineRepository
        all_machines = {m.id: m.name for m in MachineRepository.get_all_machines()}

        # Group plan by machines
        machines_plans = {}
        for plan in self.current_plan:
            machines_plans.setdefault(plan.machine_id, []).append(plan)


        fig, ax = plt.subplots(figsize=(12, 8))
        y_labels = []
        y_pos = 0
        status_colors = {
            "planned": "skyblue",
            "in_progress": "lightgreen",
            "completed": "lightgray"
        }

        for machine_id, plans in machines_plans.items():
            machine_name = all_machines.get(machine_id, f"Machine {machine_id}")
            y_labels.append(machine_name)

            for plan in plans:
                start = datetime.strptime(plan.planned_start_time, "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(plan.planned_end_time, "%Y-%m-%d %H:%M:%S")
                ax.barh(y_pos, end-start, left=start, color=status_colors.get(plan.status, "skyblue"), edgecolor='black', height=0.8)
                ax.text(start + (end-start)/2, y_pos, str(plan.order_id), va='center', ha='center', fontsize=6, color='black')

            y_pos += 1

        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontweight='bold')
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
        ax.set_xlabel("Time")
        ax.set_title("Production Plan Gantt Chart")
        plt.tight_layout()

        # Save to PDF
        pp = PdfPages(filename)
        pp.savefig(fig)
        pp.close()
        plt.close(fig)

        self.statusMessage.emit(f"PDF report exported to {filename}", "success")