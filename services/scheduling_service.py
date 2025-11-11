"""
Production scheduling service that generates production plans from pending orders.
Assigns orders to machines based on availability, priority, and deadlines.
"""

from datetime import datetime, timedelta
from typing import List, Dict
from models.order import ProductionOrderRepository
from models.machine import MachineRecipeRepository
from models.production_plan import ProductionPlan, ProductionPlanRepository


class SchedulingService:
    """Service to calculate and generate production plans for pending orders."""
    
    @staticmethod
    def _create_plan_for_orders(pending_orders: List) -> List[ProductionPlan]:
        """
        Internal helper method to create a production plan for a list of orders.
        Does not clear existing plans - caller handles that.
        
        Args:
            pending_orders: List of ProductionOrder objects to schedule
            
        Returns:
            List of ProductionPlan objects that were created
        """
        if not pending_orders:
            print("No orders to schedule.")
            return []
        
        # Dictionary to track when each machine will be free (machine_id -> datetime)
        machine_free_time: Dict[int, datetime] = {}
        
        # List to collect all newly created plans
        created_plans: List[ProductionPlan] = []
        
        # Process each order
        for order in pending_orders:
            # Get machine recipes that can produce this product
            recipes = MachineRecipeRepository.get_recipes_by_product_id(order.product_id)
            
            if not recipes:
                print(f"Warning: No machine recipe found for product {order.product_id} (Order {order.id})")
                continue
            
            # For now, assign to the first available machine
            recipe = recipes[0]
            machine_id = recipe.machine_id
            
            # Calculate production duration in hours
            duration_hours = order.quantity / recipe.production_capacity
            
            # Determine when this machine is free
            if machine_id not in machine_free_time:
                # Machine hasn't been used yet, can start immediately
                planned_start = datetime.now()
            else:
                # Machine is busy, schedule after current task
                planned_start = machine_free_time[machine_id]
            
            # Calculate planned end time
            planned_end = planned_start + timedelta(hours=duration_hours)
            
            # Create ProductionPlan object
            plan = ProductionPlan(
                id=0,
                order_id=order.id,
                machine_id=machine_id,
                planned_start_time=planned_start.strftime('%Y-%m-%d %H:%M:%S'),
                planned_end_time=planned_end.strftime('%Y-%m-%d %H:%M:%S'),
                duration_hours=round(duration_hours, 2),
                actual_start_time="",
                status="planned"
            )
            
            # Save to database
            plan = ProductionPlanRepository.add_plan(plan)
            created_plans.append(plan)
            
            # Update machine's free time for next order
            machine_free_time[machine_id] = planned_end
            
            print(f"Scheduled Order {order.id} on Machine {machine_id}: {planned_start} -> {planned_end} ({duration_hours:.2f}h)")
        
        return created_plans
    
    @staticmethod
    def generate_plan_from_scratch():
        """
        Generates a FRESH production plan from all pending orders.
        DELETES ALL existing plans (completed, in_progress, planned).
        Use this for starting completely new or clearing everything.
        
        Returns:
            List of ProductionPlan objects that were created
        """
        print("\n" + "="*80)
        print("GENERATING PRODUCTION PLAN FROM SCRATCH")
        print("="*80)
        
        # Get all pending orders
        pending_orders = ProductionOrderRepository.get_pending_orders()
        
        if not pending_orders:
            print("No pending orders to schedule.")
            return []
        
        # DELETE ALL PLANS (from scratch!)
        ProductionPlanRepository.delete_all_plans()
        print(f"Cleared all existing plans.")
        
        # Create plans for all pending orders
        created_plans = SchedulingService._create_plan_for_orders(pending_orders)
        
        print(f"\n✅ Production plan generated from scratch: {len(created_plans)} orders scheduled")
        print("="*80 + "\n")
        
        return created_plans
    
    @staticmethod
    def update_plan_with_new_orders():
        """
        Updates the EXISTING production plan with new orders.
        KEEPS: in_progress and completed orders (don't touch them)
        DELETES: only 'planned' status orders (reschedule them)
        ADDS: new pending orders to the schedule
        
        This allows adding new orders without disrupting work that's already started.
        New high-priority orders will be scheduled first.
        
        Returns:
            List of ProductionPlan objects that were created/rescheduled
        """
        print("\n" + "="*80)
        print("UPDATING PRODUCTION PLAN WITH NEW ORDERS")
        print("="*80)
        
        # Get all pending orders (old + new)
        pending_orders = ProductionOrderRepository.get_pending_orders()
        
        if not pending_orders:
            print("No pending orders to schedule.")
            return []
        
        # Get existing in_progress plans - we'll preserve their machine free times
        in_progress_plans = ProductionPlanRepository.get_plans_by_status("in_progress")
        
        # Delete only PLANNED status orders (not started yet)
        # This lets us reschedule them with new priorities
        planned_plans = ProductionPlanRepository.get_plans_by_status("planned")
        for plan in planned_plans:
            ProductionPlanRepository.delete_plan(plan)
        
        print(f"Cleared {len(planned_plans)} planned orders (will reschedule)")
        print(f"Kept {len(in_progress_plans)} in-progress orders (won't disturb)")
        
        # Build machine free times from existing in_progress orders
        machine_free_time: Dict[int, datetime] = {}
        for plan in in_progress_plans:
            # Machine will be free after this plan ends
            end_datetime = datetime.strptime(plan.planned_end_time, '%Y-%m-%d %H:%M:%S')
            if plan.machine_id not in machine_free_time:
                machine_free_time[plan.machine_id] = end_datetime
            else:
                # Take the later time if multiple plans
                machine_free_time[plan.machine_id] = max(machine_free_time[plan.machine_id], end_datetime)
        
        print(f"Machine availability snapshot taken from in-progress orders")
        
        # Create plans for all pending orders (reschedule planned + add new ones)
        # But we need to update the scheduling logic to use our machine_free_time
        created_plans = SchedulingService._create_plan_for_orders_with_constraints(
            pending_orders, 
            machine_free_time
        )
        
        print(f"\n✅ Production plan updated: {len(created_plans)} orders scheduled")
        print(f"   ({len(in_progress_plans)} in-progress orders preserved)")
        print("="*80 + "\n")
        
        return created_plans
    
    @staticmethod
    def _create_plan_for_orders_with_constraints(
        pending_orders: List, 
        initial_machine_free_time: Dict[int, datetime]
    ) -> List[ProductionPlan]:
        """
        Helper to schedule orders with existing machine constraints.
        Used when updating plan - respects already scheduled in_progress orders.
        
        Args:
            pending_orders: Orders to schedule
            initial_machine_free_time: Dict of when each machine is currently free
        """
        if not pending_orders:
            return []
        
        # Start with the provided constraints
        machine_free_time: Dict[int, datetime] = initial_machine_free_time.copy()
        created_plans: List[ProductionPlan] = []
        
        for order in pending_orders:
            recipes = MachineRecipeRepository.get_recipes_by_product_id(order.product_id)
            
            if not recipes:
                print(f"Warning: No machine recipe for product {order.product_id} (Order {order.id})")
                continue
            
            recipe = recipes[0]
            machine_id = recipe.machine_id
            duration_hours = order.quantity / recipe.production_capacity
            
            # Get when this machine is free (respecting in_progress orders)
            if machine_id not in machine_free_time:
                planned_start = datetime.now()
            else:
                planned_start = machine_free_time[machine_id]
            
            planned_end = planned_start + timedelta(hours=duration_hours)
            
            plan = ProductionPlan(
                id=0,
                order_id=order.id,
                machine_id=machine_id,
                planned_start_time=planned_start.strftime('%Y-%m-%d %H:%M:%S'),
                planned_end_time=planned_end.strftime('%Y-%m-%d %H:%M:%S'),
                duration_hours=round(duration_hours, 2),
                actual_start_time="",
                status="planned"
            )
            
            plan = ProductionPlanRepository.add_plan(plan)
            created_plans.append(plan)
            machine_free_time[machine_id] = planned_end
            
            print(f"Scheduled Order {order.id} on Machine {machine_id}: {planned_start} -> {planned_end} ({duration_hours:.2f}h)")
        
        return created_plans
    
    @staticmethod
    def get_current_plan() -> List[ProductionPlan]:
        """
        Fetches the current active production plan (all planned/in_progress tasks).
        
        Returns:
            List of ProductionPlan objects ordered by machine and start time
        """
        return ProductionPlanRepository.get_plans_for_gantt()
