from datetime import datetime
from models.order import ProductionOrderRepository
from models.machine import MachineRepository
from services.mrp_service import MRPService

class ReportsService:
    """Class responsible for fetching, filtering, and preparing report data."""

    def __init__(self):
        pass

    def get_report_data(self, report_type="orders", start_date=None, end_date=None, machine_id=None, status=None):
        """
        Returns a list of dicts with report data and a list of columns.
        - Orders: filtered by dates, machine and status.
        - Stock: full MRP result: stock, needed, shortage
        """
        if report_type.lower() == "orders":
            return self._get_filtered_orders(start_date, end_date, machine_id, status)
        elif report_type.lower() == "stock":
            return self._get_stock_data()
        else:
            return [], []

    def _get_filtered_orders(self, start_date=None, end_date=None, machine_id=None, status=None):
        """Returns orders filtered with given parameters (dates, machine, status)."""
        orders = ProductionOrderRepository.get_all_orders()
        machines = {m.id: m.name for m in MachineRepository.get_all_machines()}

        result = []
        for order in orders:
            # Start: use started_at if exists, otherwise created_at
            order_start_str = order.started_at if order.started_at else order.created_at
            order_start = datetime.strptime(order_start_str[:10], "%Y-%m-%d").date()

            # End: deadline
            order_end = datetime.strptime(order.deadline, "%Y-%m-%d").date()

            # Apply filters
            if start_date and order_start < start_date:
                continue
            if end_date and order_end > end_date:
                continue
            if machine_id and order.assigned_machine_id != machine_id:
                continue
            if status and order.status != status:
                continue

            # Duration in days
            duration_days = (order_end - order_start).days + 1

            result.append({
                "order_id": order.id,
                "machine": machines.get(order.assigned_machine_id, f"M{order.assigned_machine_id}"),
                "status": order.status,
                "start": order_start.isoformat(),
                "end": order_end.isoformat(),
                "duration": duration_days
            })

        # Columns for QTableWidget
        columns = ["Order Id", "Machine", "Status", "Start time", "End time", "Duration (h)"]
        return result, columns

    def _get_stock_data(self):
        """Returns FULL MRP material overview:
        - material
        - quantity in stock
        - quantity needed
        - shortage (negative = surplus)
        """
        mrp = MRPService.generate_procurement_plan()

        all_materials = mrp['all_materials']

        rows = []
        for m in all_materials:
            rows.append({
                "material": m.material_name,
                "stock": m.quantity_in_stock,
                "required": m.quantity_needed,
                "difference": m.quantity_difference,  # minus = surplus, plus = shortage
            })

        columns = ["Material", "In Stock", "Required", "Difference"]
        return rows, columns