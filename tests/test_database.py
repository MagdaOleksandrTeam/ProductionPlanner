"""
Test suite for database functionality using pytest.
Tests table creation, constraints, CRUD operations, and data integrity.
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path

from models import database
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM, BOMRepository
from models.machine import Machine, MachineRecipe, MachineRepository, MachineRecipeRepository
from models.order import ProductionOrder, ProductionOrderRepository
from models.production_plan import ProductionPlan, ProductionPlanRepository


@pytest.fixture
def test_db():
    """Fixture to create and cleanup test database."""
    test_dir = tempfile.mkdtemp()
    test_db_path = Path(test_dir) / "test_production.db"
    
    original_db_path = database.DB_PATH
    database.DB_PATH = test_db_path
    database._connection_manager._connection = None
    
    database.init_db()
    
    yield
    
    database.close_db()
    database.DB_PATH = original_db_path
    database._connection_manager._connection = None
    shutil.rmtree(test_dir, ignore_errors=True)


class TestTableCreation:
    """Test database initialization and table creation."""
    
    def test_all_tables_created(self, test_db):
        """Test that all tables are created correctly."""
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['materials', 'products', 'bom', 'machines', 
                         'machine_recipes', 'production_orders', 'production_plans']
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not created"


class TestConstraints:
    """Test database constraints."""
    
    def test_unique_constraint_materials(self, test_db):
        """Test UNIQUE constraint on materials.name."""
        material1 = Material(id=None, name="Steel", unit="kg", quantity=100)
        MaterialRepository.add_material(material1)
        
        with pytest.raises(sqlite3.IntegrityError):
            material2 = Material(id=None, name="Steel", unit="kg", quantity=50)
            MaterialRepository.add_material(material2)
    
    def test_unique_constraint_products(self, test_db):
        """Test UNIQUE constraint on products.name."""
        product1 = Product(id=None, name="Chair", unit="pcs", description="Wooden")
        ProductRepository.add_product(product1)
        
        with pytest.raises(sqlite3.IntegrityError):
            product2 = Product(id=None, name="Chair", unit="pcs", description="Metal")
            ProductRepository.add_product(product2)
    
    def test_check_constraint_quantity(self, test_db):
        """Test CHECK constraint on quantity > 0."""
        product = Product(id=None, name="Table", unit="pcs", description="Test")
        ProductRepository.add_product(product)
        
        with pytest.raises(sqlite3.IntegrityError):
            order = ProductionOrder(
                id=None, product_id=product.id, quantity=0,
                deadline="2025-12-31", status="in_queue", priority=1
            )
            ProductionOrderRepository.add_order(order)
    
    def test_check_constraint_status(self, test_db):
        """Test CHECK constraint on status values."""
        product = Product(id=None, name="Widget", unit="pcs", description="Test")
        ProductRepository.add_product(product)
        
        with pytest.raises(sqlite3.IntegrityError):
            order = ProductionOrder(
                id=None, product_id=product.id, quantity=10,
                deadline="2025-12-31", status="invalid_status", priority=1
            )
            ProductionOrderRepository.add_order(order)
    
    def test_foreign_key_cascade(self, test_db):
        """Test FOREIGN KEY CASCADE on delete."""
        product = Product(id=None, name="Gadget", unit="pcs", description="Test")
        ProductRepository.add_product(product)
        
        material = Material(id=None, name="Aluminum", unit="kg", quantity=100)
        MaterialRepository.add_material(material)
        
        bom = BOM(id=None, product_id=product.id, material_id=material.id, quantity_needed=5.0)
        BOMRepository.add_bom(bom)
        
        # Delete product - should cascade to BOM
        ProductRepository.delete_product(product)
        
        bom_entries = BOMRepository.get_all_bom()
        assert len(bom_entries) == 0, "CASCADE DELETE failed"
    
    def test_bom_unique_constraint(self, test_db):
        """Test UNIQUE constraint on (product_id, material_id) in BOM."""
        product = Product(id=None, name="Bicycle", unit="pcs", description="Test")
        ProductRepository.add_product(product)
        
        material = Material(id=None, name="Steel", unit="kg", quantity=100)
        MaterialRepository.add_material(material)
        
        bom1 = BOM(id=None, product_id=product.id, material_id=material.id, quantity_needed=1.0)
        BOMRepository.add_bom(bom1)
        
        with pytest.raises(sqlite3.IntegrityError):
            bom2 = BOM(id=None, product_id=product.id, material_id=material.id, quantity_needed=5.0)
            BOMRepository.add_bom(bom2)


class TestCRUDOperations:
    """Test Create, Read, Update, Delete operations."""
    
    def test_material_crud(self, test_db):
        """Test CRUD operations on materials."""
        # CREATE
        material = Material(id=None, name="Copper", unit="kg", quantity=50.5)
        material = MaterialRepository.add_material(material)
        assert material.id is not None
        
        # READ
        retrieved = MaterialRepository.get_material_by_id(material.id)
        assert retrieved is not None
        assert retrieved.name == "Copper"
        assert retrieved.quantity == 50.5
        
        # UPDATE
        material.quantity = 75.0
        MaterialRepository.update_material(material)
        updated = MaterialRepository.get_material_by_id(material.id)
        assert updated.quantity == 75.0
        
        # DELETE
        MaterialRepository.delete_material(material)
        deleted = MaterialRepository.get_material_by_id(material.id)
        assert deleted is None
    
    def test_product_crud(self, test_db):
        """Test CRUD operations on products."""
        # CREATE
        product = Product(id=None, name="Gear", unit="pcs", description="Metal gear")
        product = ProductRepository.add_product(product)
        assert product.id is not None
        
        # READ
        retrieved = ProductRepository.get_product_by_id(product.id)
        assert retrieved is not None
        assert retrieved.name == "Gear"
        
        # UPDATE
        product.description = "Updated description"
        ProductRepository.update_product(product)
        updated = ProductRepository.get_product_by_id(product.id)
        assert updated.description == "Updated description"
        
        # DELETE
        ProductRepository.delete_product(product)
        deleted = ProductRepository.get_product_by_id(product.id)
        assert deleted is None
    
    def test_order_crud(self, test_db):
        """Test CRUD operations on production orders."""
        # Create product first (FK requirement)
        product = Product(id=None, name="Widget", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        # CREATE
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=100,
            deadline="2025-12-31", status="in_queue", priority=1
        )
        order = ProductionOrderRepository.add_order(order)
        assert order.id is not None
        
        # READ
        retrieved = ProductionOrderRepository.get_order_by_id(order.id)
        assert retrieved is not None
        assert retrieved.quantity == 100
        assert retrieved.status == "in_queue"
        
        # UPDATE
        order.status = "in_progress"
        order.quantity = 150
        ProductionOrderRepository.update_order(order)
        updated = ProductionOrderRepository.get_order_by_id(order.id)
        assert updated.status == "in_progress"
        assert updated.quantity == 150
        
        # DELETE
        ProductionOrderRepository.delete_order(order)
        deleted = ProductionOrderRepository.get_order_by_id(order.id)
        assert deleted is None
    
    def test_machine_crud(self, test_db):
        """Test CRUD operations on machines."""
        # CREATE
        machine = Machine(id=None, name="CNC Lathe")
        machine = MachineRepository.add_machine(machine)
        assert machine.id is not None
        
        # READ
        retrieved = MachineRepository.get_machine_by_id(machine.id)
        assert retrieved is not None
        assert retrieved.name == "CNC Lathe"
        
        # UPDATE
        machine.name = "CNC Lathe Pro"
        MachineRepository.update_machine(machine)
        updated = MachineRepository.get_machine_by_id(machine.id)
        assert updated.name == "CNC Lathe Pro"
        
        # DELETE
        MachineRepository.delete_machine(machine)
        deleted = MachineRepository.get_machine_by_id(machine.id)
        assert deleted is None


class TestDataIntegrity:
    """Test data integrity and business logic."""
    
    def test_bom_relationships(self, test_db):
        """Test BOM relationships between products and materials."""
        product = Product(id=None, name="Bicycle", unit="pcs", description="Mountain bike")
        product = ProductRepository.add_product(product)
        
        material1 = Material(id=None, name="Steel Frame", unit="pcs", quantity=10)
        material1 = MaterialRepository.add_material(material1)
        
        material2 = Material(id=None, name="Rubber Tire", unit="pcs", quantity=50)
        material2 = MaterialRepository.add_material(material2)
        
        # Create BOM entries
        bom1 = BOM(id=None, product_id=product.id, material_id=material1.id, quantity_needed=1.0)
        BOMRepository.add_bom(bom1)
        
        bom2 = BOM(id=None, product_id=product.id, material_id=material2.id, quantity_needed=2.0)
        BOMRepository.add_bom(bom2)
        
        # Retrieve BOM for product
        bom_entries = BOMRepository.get_bom_by_product_id(product.id)
        assert len(bom_entries) == 2
        
        # Verify quantities
        quantities = {entry.material_id: entry.quantity_needed for entry in bom_entries}
        assert quantities[material1.id] == 1.0
        assert quantities[material2.id] == 2.0
    
    def test_machine_recipes(self, test_db):
        """Test machine recipe relationships."""
        machine = Machine(id=None, name="CNC Mill")
        machine = MachineRepository.add_machine(machine)
        
        product = Product(id=None, name="Gear", unit="pcs", description="Metal gear")
        product = ProductRepository.add_product(product)
        
        # Create recipe
        recipe = MachineRecipe(
            id=None, machine_id=machine.id, 
            product_id=product.id, production_capacity=10.0
        )
        recipe = MachineRecipeRepository.add_machine_recipe(recipe)
        
        # Retrieve recipes
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(machine.id)
        assert len(recipes) == 1
        assert recipes[0].production_capacity == 10.0
        
        # Retrieve by product
        recipes_by_product = MachineRecipeRepository.get_recipes_by_product_id(product.id)
        assert len(recipes_by_product) == 1
        assert recipes_by_product[0].machine_id == machine.id
    
    def test_production_plan_creation(self, test_db):
        """Test production plan creation and relationships."""
        # Setup
        machine = Machine(id=None, name="Assembly Line")
        machine = MachineRepository.add_machine(machine)
        
        product = Product(id=None, name="Widget", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=100,
            deadline="2025-12-31", status="in_queue", priority=1
        )
        order = ProductionOrderRepository.add_order(order)
        
        # Create production plan
        plan = ProductionPlan(
            id=None, order_id=order.id, machine_id=machine.id,
            planned_start_time="2025-11-26 08:00:00",
            planned_end_time="2025-11-26 18:00:00",
            duration_hours=10.0, status="planned"
        )
        plan = ProductionPlanRepository.add_plan(plan)
        
        assert plan.id is not None
        
        # Retrieve by order
        plans = ProductionPlanRepository.get_plans_by_order_id(order.id)
        assert len(plans) == 1
        assert plans[0].duration_hours == 10.0
        
        # Retrieve by machine
        machine_plans = ProductionPlanRepository.get_plans_by_machine_id(machine.id)
        assert len(machine_plans) == 1
    
    def test_search_materials_by_name(self, test_db):
        """Test search functionality for materials."""
        MaterialRepository.add_material(Material(id=None, name="Steel Rod", unit="m", quantity=100))
        MaterialRepository.add_material(Material(id=None, name="Steel Plate", unit="kg", quantity=50))
        MaterialRepository.add_material(Material(id=None, name="Aluminum Rod", unit="m", quantity=75))
        
        # Search for "Steel"
        results = MaterialRepository.search_materials_by_name("Steel")
        assert len(results) == 2
        
        # Search for "Rod"
        results = MaterialRepository.search_materials_by_name("Rod")
        assert len(results) == 2
        
        # Search for "Plate"
        results = MaterialRepository.search_materials_by_name("Plate")
        assert len(results) == 1
    
    def test_get_orders_by_status(self, test_db):
        """Test filtering orders by status."""
        product = Product(id=None, name="Test Product", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        # Create orders with different statuses
        order1 = ProductionOrder(
            id=None, product_id=product.id, quantity=10,
            deadline="2025-12-31", status="in_queue", priority=1
        )
        ProductionOrderRepository.add_order(order1)
        
        order2 = ProductionOrder(
            id=None, product_id=product.id, quantity=20,
            deadline="2025-12-31", status="in_progress", priority=2
        )
        ProductionOrderRepository.add_order(order2)
        
        order3 = ProductionOrder(
            id=None, product_id=product.id, quantity=30,
            deadline="2025-12-31", status="completed", priority=3
        )
        ProductionOrderRepository.add_order(order3)
        
        # Test filtering
        in_queue = ProductionOrderRepository.get_orders_by_status("in_queue")
        assert len(in_queue) == 1
        assert in_queue[0].quantity == 10
        
        in_progress = ProductionOrderRepository.get_orders_by_status("in_progress")
        assert len(in_progress) == 1
        assert in_progress[0].quantity == 20
        
        completed = ProductionOrderRepository.get_orders_by_status("completed")
        assert len(completed) == 1
        assert completed[0].quantity == 30


class TestUnitMaterial:
    """Unit tests for Material class and operations."""
    
    def test_material_creation(self, test_db):
        """Test correct Material object creation."""
        material = Material(id=None, name="Wood", unit="m3", quantity=25.5)
        assert material.name == "Wood"
        assert material.unit == "m3"
        assert material.quantity == 25.5
    
    def test_material_validation_name(self, test_db):
        """Test validation of material data - duplicate name should fail."""
        material1 = Material(id=None, name="Iron", unit="kg", quantity=10)
        MaterialRepository.add_material(material1)
        
        # Try to add duplicate name
        with pytest.raises(sqlite3.IntegrityError):
            material2 = Material(id=None, name="Iron", unit="kg", quantity=20)
            MaterialRepository.add_material(material2)
    
    def test_material_quantity_update(self, test_db):
        """Test updating material quantity in stock."""
        material = Material(id=None, name="Plastic", unit="kg", quantity=100)
        material = MaterialRepository.add_material(material)
        
        # Update quantity
        material.quantity = 150
        MaterialRepository.update_material(material)
        
        updated = MaterialRepository.get_material_by_id(material.id)
        assert updated.quantity == 150


class TestUnitProductionOrder:
    """Unit tests for ProductionOrder class and operations."""
    
    def test_order_creation(self, test_db):
        """Test correct ProductionOrder object creation."""
        product = Product(id=None, name="TestProd", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=50,
            deadline="2026-02-15", status="in_queue", priority=1
        )
        order = ProductionOrderRepository.add_order(order)
        
        assert order.id is not None
        assert order.quantity == 50
        assert order.status == "in_queue"
    
    def test_order_validation_quantity(self, test_db):
        """Test validation - quantity must be positive."""
        product = Product(id=None, name="Widget2", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        # Negative quantity should fail
        with pytest.raises(sqlite3.IntegrityError):
            order = ProductionOrder(
                id=None, product_id=product.id, quantity=-5,
                deadline="2026-02-15", status="in_queue", priority=1
            )
            ProductionOrderRepository.add_order(order)
    
    def test_order_status_change(self, test_db):
        """Test changing order status from in_queue to in_progress."""
        product = Product(id=None, name="Item", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=25,
            deadline="2026-03-01", status="in_queue", priority=2
        )
        order = ProductionOrderRepository.add_order(order)
        
        # Change status
        order.status = "in_progress"
        ProductionOrderRepository.update_order(order)
        
        updated = ProductionOrderRepository.get_order_by_id(order.id)
        assert updated.status == "in_progress"


class TestUnitMRPService:
    """Unit tests for MRP service calculations."""
    
    def test_mrp_no_orders(self, test_db):
        """Test MRP with no pending orders."""
        from services.mrp_service import MRPService
        
        requirements = MRPService.calculate_material_requirements()
        assert len(requirements) == 0
    
    def test_mrp_with_order_and_bom(self, test_db):
        """Test MRP calculation with order and BOM."""
        from services.mrp_service import MRPService
        
        # Create material
        material = Material(id=None, name="Steel", unit="kg", quantity=10)
        material = MaterialRepository.add_material(material)
        
        # Create product
        product = Product(id=None, name="Part", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        # Create BOM
        from models.bom import BOM, BOMRepository
        bom = BOM(id=None, product_id=product.id, material_id=material.id, quantity_needed=2.0)
        BOMRepository.add_bom(bom)
        
        # Create order
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=10,
            deadline="2026-02-20", status="in_queue", priority=1
        )
        ProductionOrderRepository.add_order(order)
        
        # Calculate requirements
        requirements = MRPService.calculate_material_requirements()
        
        # Should find requirements for Steel
        assert len(requirements) > 0
        steel_req = next((r for r in requirements if r.material_name == "Steel"), None)
        assert steel_req is not None
        assert steel_req.quantity_needed == 20.0  # 10 parts * 2 kg each


class TestUnitSchedulingService:
    """Unit tests for Scheduling service."""
    
    def test_scheduling_no_orders(self, test_db):
        """Test scheduling with no pending orders."""
        from services.scheduling_service import SchedulingService
        
        plans = SchedulingService.generate_plan_from_scratch()
        assert len(plans) == 0
    
    def test_scheduling_assigns_machine(self, test_db):
        """Test that scheduling assigns orders to machines."""
        from services.scheduling_service import SchedulingService
        from models.machine import Machine, MachineRecipe, MachineRepository, MachineRecipeRepository
        
        # Create machine
        machine = Machine(id=None, name="Machine1")
        machine = MachineRepository.add_machine(machine)
        
        # Create product
        product = Product(id=None, name="Widget", unit="pcs", description="Test")
        product = ProductRepository.add_product(product)
        
        # Create recipe
        recipe = MachineRecipe(
            id=None, machine_id=machine.id, 
            product_id=product.id, production_capacity=5.0
        )
        MachineRecipeRepository.add_machine_recipe(recipe)
        
        # Create order
        order = ProductionOrder(
            id=None, product_id=product.id, quantity=10,
            deadline="2026-02-25", status="in_queue", priority=1
        )
        ProductionOrderRepository.add_order(order)
        
        # Generate schedule
        plans = SchedulingService.generate_plan_from_scratch()
        
        # Should create at least one plan
        assert len(plans) > 0
        assert plans[0].machine_id == machine.id
        assert plans[0].order_id == order.id
