from datetime import date
from models.product import ProductRepository
from models.order import ProductionOrderRepository

class DashboardService:
    """Service to prepare data for the Dashboard view (KPI and table)."""

    @staticmethod
    def get_kpi_counts():
        # Count orders by status
        pending = len(ProductionOrderRepository.get_orders_by_status("in_queue"))
        in_progress = len(ProductionOrderRepository.get_orders_by_status("in_progress"))
        completed = len(ProductionOrderRepository.get_orders_by_status("completed"))

        # Count late orders (deadline passed but not completed)
        today = date.today().isoformat()
        all_orders = ProductionOrderRepository.get_all_orders()
        late_orders = len([o for o in all_orders if o.deadline < today and o.status != "completed"])

        # Count queued orders by priority (1=High, 2=Medium, 3=Low)
        queued_orders = [o.priority for o in all_orders if o.status == "in_queue"]
        priority_count = {1: 0, 2: 0, 3: 0}
        for p in queued_orders:
            if p in priority_count:
                priority_count[p] += 1
        
        return {
            # Numeric values for KPI
            "pending_orders": pending,
            "orders_in_progress": in_progress,
            "completed_orders": completed,
            "late_orders": late_orders,
            "queued_orders_by_priority": priority_count,

            # Labels with icons for display
            "pending_label": "🕒 Pending Orders",
            "in_progress_label": "⚙️ Orders in Progress",
            "completed_label": "✅ Completed Orders",
            "late_label": "⏰ Late Orders",

            "priority_high_label": "🔴 High",
            "priority_medium_label": "🟡 Medium",
            "priority_low_label": "🟢 Low"
        }
        
    @staticmethod
    def priority_icon(priority: int) -> str:
        # Return colored icon for priority
        if priority == 1:
            return "🔴"
        elif priority == 2:
            return "🟡"
        else:
            return "🟢"

    @staticmethod
    def get_orders_status_overview():
        """Return orders with product names and priority icon for table view."""
        orders = ProductionOrderRepository.get_all_orders()
        table_data = []

        for o in orders:
            # Get product name by ID
            product = ProductRepository.get_product_by_id(o.product_id)
            product_name = product.name if product else f"Product {o.product_id}"
            
            table_data.append({
                "order_id": o.id,
                "product": product_name,
                "quantity": o.quantity,
                "priority": DashboardService.priority_icon(o.priority),  # icon for priority
                "status": o.status,
                "deadline": o.deadline
            })
        return table_data