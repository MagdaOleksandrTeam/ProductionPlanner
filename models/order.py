from . import database
from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import date

class OrderStatus(Enum):
    IN_QUEUE = "in_queue"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class OrderPriority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class ProductionOrder():
    id: int
    product_id: int
    quantity: int
    deadline: str  # Date string in format 'YYYY-MM-DD'
    status: str
    priority: int
    created_at: str = ""  # Date string in format 'YYYY-MM-DD'
    assigned_machine_id: int = None  # FK to machines, nullable
    started_at: str = ""  # DateTime string, nullable - when production actually started
    
    def __str__(self) -> str:
        machine_info = f", Machine: {self.assigned_machine_id}" if self.assigned_machine_id else ""
        started_info = f", Started: {self.started_at}" if self.started_at else ""
        return f"ProductionOrder(ID: {self.id}, Product ID: {self.product_id}, Quantity: {self.quantity}, Deadline: {self.deadline}, Status: {self.status}, Priority: {self.priority}, Created: {self.created_at}{machine_info}{started_info})"


class ProductionOrderRepository:
    @staticmethod
    def init_table():
        """Creates the production_orders table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS production_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    deadline DATE NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('in_queue', 'in_progress', 'completed')),
                    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
                    created_at DATE DEFAULT (date('now')),
                    assigned_machine_id INTEGER,
                    started_at DATETIME,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_machine_id) REFERENCES machines(id) ON DELETE SET NULL
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_order(order: ProductionOrder):
        """Adds a new production order to the database. Returns the order with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO production_orders (product_id, quantity, deadline, status, priority, assigned_machine_id, started_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order.product_id, order.quantity, order.deadline, order.status, order.priority, 
                  order.assigned_machine_id, order.started_at if order.started_at else None))
            conn.commit()
            order.id = cursor.lastrowid
            # Get the created_at value that was set by the database
            cursor.execute("SELECT created_at FROM production_orders WHERE id = ?", (order.id,))
            order.created_at = cursor.fetchone()[0]
        return order

    @staticmethod
    def get_order_by_id(order_id: int) -> ProductionOrder:
        """Fetches a production order by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders WHERE id = ?
            """, (order_id,))
            row = cursor.fetchone()
            if row:
                return ProductionOrder(
                    id=row[0], product_id=row[1], quantity=row[2], 
                    deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                    assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
                )
            return None
    
    @staticmethod
    def get_orders_by_product_id(product_id: int) -> List[ProductionOrder]:
        """Fetches all production orders for a specific product."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders WHERE product_id = ?
                ORDER BY deadline, priority
            """, (product_id,))
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
    
    @staticmethod
    def get_orders_by_status(status: str) -> List[ProductionOrder]:
        """Fetches all production orders with a specific status."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders WHERE status = ?
                ORDER BY deadline, priority
            """, (status,))
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
    
    @staticmethod
    def get_orders_by_priority(priority: int) -> List[ProductionOrder]:
        """Fetches all production orders with a specific priority."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders WHERE priority = ?
                ORDER BY deadline
            """, (priority,))
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
        
    @staticmethod
    def update_order(order: ProductionOrder):
        """Updates an existing production order in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE production_orders 
                SET product_id = ?, quantity = ?, deadline = ?, status = ?, priority = ?, 
                    assigned_machine_id = ?, started_at = ?
                WHERE id = ?
            """, (order.product_id, order.quantity, order.deadline, order.status, order.priority, 
                  order.assigned_machine_id, order.started_at if order.started_at else None, order.id))
            conn.commit()

    @staticmethod
    def delete_order(order: ProductionOrder):
        """Deletes a production order from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM production_orders WHERE id = ?", (order.id,))
            conn.commit()
    
    @staticmethod
    def get_all_orders() -> List[ProductionOrder]:
        """Returns all production orders from the database, ordered by deadline and priority."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders 
                ORDER BY deadline, priority
            """)
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
    
    @staticmethod
    def get_pending_orders() -> List[ProductionOrder]:
        """Returns all orders that are not yet completed (in_queue or in_progress)."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders 
                WHERE status != 'completed'
                ORDER BY deadline, priority
            """)
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
    
    @staticmethod
    def get_orders_by_machine_id(machine_id: int) -> List[ProductionOrder]:
        """Fetches all production orders assigned to a specific machine."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, quantity, deadline, status, priority, created_at, assigned_machine_id, started_at 
                FROM production_orders 
                WHERE assigned_machine_id = ?
                ORDER BY started_at DESC
            """, (machine_id,))
            rows = cursor.fetchall()
            return [ProductionOrder(
                id=row[0], product_id=row[1], quantity=row[2], 
                deadline=row[3], status=row[4], priority=row[5], created_at=row[6],
                assigned_machine_id=row[7], started_at=row[8] if row[8] else ""
            ) for row in rows]
    
    @staticmethod
    def print_all_orders():
        """Prints all production orders in a formatted way. Just for demo purposes."""
        orders = ProductionOrderRepository.get_all_orders()
        if not orders:
            print("No production orders found in the database.")
            return
        
        print(f"\n{'='*80}")
        print(f"{'PRODUCTION ORDERS LIST':^80}")
        print(f"{'='*80}")
        for order in orders:
            print(order)
        print(f"{'='*80}")
        print(f"Total orders: {len(orders)}")
        print()
