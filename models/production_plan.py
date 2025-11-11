from . import database
from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import datetime

class PlanStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class ProductionPlan():
    id: int
    order_id: int  # FK to production_orders - which order this plan is for
    machine_id: int  # FK to machines - which machine will execute this order
    planned_start_time: str  # DateTime string in format 'YYYY-MM-DD HH:MM:SS' - calculated when machine becomes free
    planned_end_time: str  # DateTime string in format 'YYYY-MM-DD HH:MM:SS' - calculated as planned_start_time + duration_hours
    duration_hours: float  # How long the operation takes in hours (comes from machine recipe or BOM)
    actual_start_time: str = ""  # DateTime string, nullable - when production actually started (updates when work begins)
    status: str = "planned"  # Current status: planned, in_progress, or completed
    created_at: str = ""  # DateTime string in format 'YYYY-MM-DD HH:MM:SS' - when this plan was calculated/created
    
    def __str__(self) -> str:
        actual_info = f", Actual Start: {self.actual_start_time}" if self.actual_start_time else ""
        return f"ProductionPlan(ID: {self.id}, Order ID: {self.order_id}, Machine ID: {self.machine_id}, Planned: {self.planned_start_time} -> {self.planned_end_time}, Duration: {self.duration_hours}h, Status: {self.status}, Created: {self.created_at}{actual_info})"


class ProductionPlanRepository:
    @staticmethod
    def init_table():
        """Creates the production_plans table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS production_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    machine_id INTEGER NOT NULL,
                    planned_start_time DATETIME NOT NULL,
                    planned_end_time DATETIME NOT NULL,
                    duration_hours REAL NOT NULL CHECK(duration_hours > 0),
                    actual_start_time DATETIME,
                    status TEXT NOT NULL CHECK(status IN ('planned', 'in_progress', 'completed')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES production_orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_plan(plan: ProductionPlan):
        """Adds a new production plan to the database. Returns the plan with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO production_plans (order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (plan.order_id, plan.machine_id, plan.planned_start_time, plan.planned_end_time, 
                  plan.duration_hours, plan.actual_start_time if plan.actual_start_time else None, plan.status))
            conn.commit()
            plan.id = cursor.lastrowid
            # Get the created_at value that was set by the database
            cursor.execute("SELECT created_at FROM production_plans WHERE id = ?", (plan.id,))
            plan.created_at = cursor.fetchone()[0]
        return plan

    @staticmethod
    def get_plan_by_id(plan_id: int) -> ProductionPlan:
        """Fetches a production plan by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans WHERE id = ?
            """, (plan_id,))
            row = cursor.fetchone()
            if row:
                return ProductionPlan(
                    id=row[0], order_id=row[1], machine_id=row[2], 
                    planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                    actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
                )
            return None
    
    @staticmethod
    def get_plans_by_order_id(order_id: int) -> List[ProductionPlan]:
        """Fetches all production plans for a specific order."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans WHERE order_id = ?
                ORDER BY planned_start_time
            """, (order_id,))
            rows = cursor.fetchall()
            return [ProductionPlan(
                id=row[0], order_id=row[1], machine_id=row[2], 
                planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
            ) for row in rows]
    
    @staticmethod
    def get_plans_by_machine_id(machine_id: int) -> List[ProductionPlan]:
        """Fetches all production plans assigned to a specific machine, ordered by planned start time."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans WHERE machine_id = ?
                ORDER BY planned_start_time
            """, (machine_id,))
            rows = cursor.fetchall()
            return [ProductionPlan(
                id=row[0], order_id=row[1], machine_id=row[2], 
                planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
            ) for row in rows]
    
    @staticmethod
    def get_plans_by_status(status: str) -> List[ProductionPlan]:
        """Fetches all production plans with a specific status."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans WHERE status = ?
                ORDER BY planned_start_time
            """, (status,))
            rows = cursor.fetchall()
            return [ProductionPlan(
                id=row[0], order_id=row[1], machine_id=row[2], 
                planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
            ) for row in rows]
    
    @staticmethod
    def get_all_plans() -> List[ProductionPlan]:
        """Returns all production plans from the database, ordered by planned start time."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans 
                ORDER BY planned_start_time
            """)
            rows = cursor.fetchall()
            return [ProductionPlan(
                id=row[0], order_id=row[1], machine_id=row[2], 
                planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
            ) for row in rows]
    
    @staticmethod
    def update_plan(plan: ProductionPlan):
        """Updates an existing production plan in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE production_plans 
                SET order_id = ?, machine_id = ?, planned_start_time = ?, planned_end_time = ?, 
                    duration_hours = ?, actual_start_time = ?, status = ?
                WHERE id = ?
            """, (plan.order_id, plan.machine_id, plan.planned_start_time, plan.planned_end_time, 
                  plan.duration_hours, plan.actual_start_time if plan.actual_start_time else None, 
                  plan.status, plan.id))
            conn.commit()

    @staticmethod
    def delete_plan(plan: ProductionPlan):
        """Deletes a production plan from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM production_plans WHERE id = ?", (plan.id,))
            conn.commit()
    
    @staticmethod
    def delete_plans_by_order_id(order_id: int):
        """Deletes all production plans for a specific order (useful when recalculating)."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM production_plans WHERE order_id = ?", (order_id,))
            conn.commit()
    
    @staticmethod
    def delete_all_plans():
        """Deletes all production plans from the database. Used when generating a fresh plan."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM production_plans")
            conn.commit()
    
    @staticmethod
    def get_plans_for_gantt() -> List[ProductionPlan]:
        """Returns all planned/in_progress plans for Gantt view, ordered by machine and start time."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, order_id, machine_id, planned_start_time, planned_end_time, duration_hours, actual_start_time, status, created_at 
                FROM production_plans 
                WHERE status IN ('planned', 'in_progress')
                ORDER BY machine_id, planned_start_time
            """)
            rows = cursor.fetchall()
            return [ProductionPlan(
                id=row[0], order_id=row[1], machine_id=row[2], 
                planned_start_time=row[3], planned_end_time=row[4], duration_hours=row[5],
                actual_start_time=row[6] if row[6] else "", status=row[7], created_at=row[8]
            ) for row in rows]
    
    @staticmethod
    def print_all_plans():
        """Prints all production plans in a formatted way. Just for demo purposes."""
        plans = ProductionPlanRepository.get_all_plans()
        if not plans:
            print("No production plans found in the database.")
            return
        
        print(f"\n{'='*100}")
        print(f"{'PRODUCTION PLANS LIST':^100}")
        print(f"{'='*100}")
        for plan in plans:
            print(plan)
        print(f"{'='*100}")
        print(f"Total plans: {len(plans)}")
        print()
