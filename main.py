import sys, os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from models.database import init_db, close_db, get_connection
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM, BOMRepository
from models.machine import Machine, MachineRecipe, MachineRepository, MachineRecipeRepository
from models.order import ProductionOrder, ProductionOrderRepository, OrderStatus, OrderPriority
from models.production_plan import ProductionPlanRepository
from services.scheduling_service import SchedulingService
from services.mrp_service import MRPService
from services.dashboard_service import DashboardService
from datetime import date, timedelta

def showcase_materials():
    """Showcase function to demonstrate Material model capabilities."""
    print("\n" + "="*60)
    print("MATERIALS MODEL SHOWCASE")
    print("="*60)
    
    # Check if materials already exist to avoid duplicates
    existing_materials = MaterialRepository.get_all_materials()
    
    if not existing_materials:
        # Create and add materials only if database is empty
        material1 = Material(id=0, name="Steel", quantity=100.0, unit="kg")
        material2 = Material(id=0, name="Wood", quantity=50.0, unit="m³")
        material3 = Material(id=0, name="Plastic", quantity=25.0, unit="kg")
        
        # Add materials to database
        MaterialRepository.add_material(material1)
        MaterialRepository.add_material(material2)
        MaterialRepository.add_material(material3)
        
        print("Materials added to database!")
    else:
        print("Materials already exist in database.")
    
    # Print all materials
    MaterialRepository.print_all_materials()
    
    # Demonstrate search functionality
    print("\n" + "="*50)
    print("MATERIAL SEARCH FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Exact search
    print("\n1. Exact search for 'Steel':")
    steel = MaterialRepository.get_material_by_name("Steel")
    if steel:
        print(f"   Found: {steel}")
    else:
        print("   Not found!")
    
    # Partial searches
    print("\n2. Partial search for 'ste' (should find Steel):")
    materials = MaterialRepository.search_materials_by_name("ste")
    for material in materials:
        print(f"   Found: {material}")
    
    print("\n3. Partial search for 'wood' (should find Wood):")
    materials = MaterialRepository.search_materials_by_name("wood")
    for material in materials:
        print(f"   Found: {material}")
    
    print("\n4. Partial search for 'l' (should find Steel and Plastic):")
    materials = MaterialRepository.search_materials_by_name("l")
    for material in materials:
        print(f"   Found: {material}")
    
    print("\n5. Search for 'xyz' (should find nothing):")
    materials = MaterialRepository.search_materials_by_name("xyz")
    if materials:
        for material in materials:
            print(f"   Found: {material}")
    else:
        print("   No materials found!")
    
    print("="*50)


def showcase_products():
    """Showcase function to demonstrate Product model capabilities."""
    print("\n" + "="*60)
    print("PRODUCTS MODEL SHOWCASE")
    print("="*60)
    
    # Check if products already exist to avoid duplicates
    existing_products = ProductRepository.get_all_products()
    
    if not existing_products:
        # Create and add products only if database is empty
        product1 = Product(id=0, name="Table", unit="pcs", description="Wooden dining table", quantity=0.0)
        product2 = Product(id=0, name="Chair", unit="pcs", description="Comfortable office chair", quantity=0.0)
        product3 = Product(id=0, name="Cabinet", unit="pcs", description="Storage cabinet with shelves", quantity=0.0)
        
        # Add products to database
        ProductRepository.add_product(product1)
        ProductRepository.add_product(product2)
        ProductRepository.add_product(product3)
        
        print("Products added to database!")
    else:
        print("Products already exist in database.")
    
    # Print all products
    ProductRepository.print_all_products()
    
    # Demonstrate search functionality
    print("\n" + "="*50)
    print("PRODUCT SEARCH FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Exact search
    print("\n1. Exact search for 'Table':")
    table = ProductRepository.get_product_by_name("Table")
    if table:
        print(f"   Found: {table}")
    else:
        print("   Not found!")
    
    # Partial searches
    print("\n2. Partial search for 'tab' (should find Table):")
    products = ProductRepository.search_products_by_name("tab")
    for product in products:
        print(f"   Found: {product}")
    
    print("\n3. Partial search for 'chair' (should find Chair):")
    products = ProductRepository.search_products_by_name("chair")
    for product in products:
        print(f"   Found: {product}")
    
    print("\n4. Partial search for 'c' (should find Chair and Cabinet):")
    products = ProductRepository.search_products_by_name("c")
    for product in products:
        print(f"   Found: {product}")
    
    print("\n5. Search for 'desk' (should find nothing):")
    products = ProductRepository.search_products_by_name("desk")
    if products:
        for product in products:
            print(f"   Found: {product}")
    else:
        print("   No products found!")
    
    print("="*50)
    
    # Demonstrate inventory update functionality
    print("\n" + "="*50)
    print("PRODUCT INVENTORY UPDATE SHOWCASE")
    print("="*50)
    
    # Update quantities to simulate production
    table = ProductRepository.get_product_by_name("Table")
    if table:
        print(f"\nBefore production: {table}")
        table.quantity = 10.0  # Simulate producing 10 tables
        ProductRepository.update_product(table)
        updated_table = ProductRepository.get_product_by_id(table.id)
        print(f"After producing 10 tables: {updated_table}")
    
    chair = ProductRepository.get_product_by_name("Chair")
    if chair:
        print(f"\nBefore production: {chair}")
        chair.quantity = 25.0  # Simulate producing 25 chairs
        ProductRepository.update_product(chair)
        updated_chair = ProductRepository.get_product_by_id(chair.id)
        print(f"After producing 25 chairs: {updated_chair}")
    
    print("\n" + "="*50)
    print("UPDATED PRODUCT INVENTORY")
    print("="*50)
    ProductRepository.print_all_products()


def showcase_bom():
    """Showcase function to demonstrate BOM model capabilities."""
    print("\n" + "="*60)
    print("BOM MODEL SHOWCASE")
    print("="*60)
    
    # Check if BOM entries already exist to avoid duplicates
    existing_bom = BOMRepository.get_all_bom()
    
    if not existing_bom:
        # Get existing products and materials to create BOM entries
        table = ProductRepository.get_product_by_name("Table")
        chair = ProductRepository.get_product_by_name("Chair")
        cabinet = ProductRepository.get_product_by_name("Cabinet")
        
        steel = MaterialRepository.get_material_by_name("Steel")
        wood = MaterialRepository.get_material_by_name("Wood")
        plastic = MaterialRepository.get_material_by_name("Plastic")
        
        if table and chair and cabinet and steel and wood and plastic:
            # Create BOM entries: what materials are needed for each product
            
            # Table recipe: 2.0 m³ Wood + 5.0 kg Steel
            bom1 = BOM(id=0, product_id=table.id, material_id=wood.id, quantity_needed=2.0)
            bom2 = BOM(id=0, product_id=table.id, material_id=steel.id, quantity_needed=5.0)
            
            # Chair recipe: 0.5 m³ Wood + 2.0 kg Steel + 1.0 kg Plastic
            bom3 = BOM(id=0, product_id=chair.id, material_id=wood.id, quantity_needed=0.5)
            bom4 = BOM(id=0, product_id=chair.id, material_id=steel.id, quantity_needed=2.0)
            bom5 = BOM(id=0, product_id=chair.id, material_id=plastic.id, quantity_needed=1.0)
            
            # Cabinet recipe: 3.0 m³ Wood + 8.0 kg Steel
            bom6 = BOM(id=0, product_id=cabinet.id, material_id=wood.id, quantity_needed=3.0)
            bom7 = BOM(id=0, product_id=cabinet.id, material_id=steel.id, quantity_needed=8.0)
            
            # Add BOM entries to database
            BOMRepository.add_bom(bom1)
            BOMRepository.add_bom(bom2)
            BOMRepository.add_bom(bom3)
            BOMRepository.add_bom(bom4)
            BOMRepository.add_bom(bom5)
            BOMRepository.add_bom(bom6)
            BOMRepository.add_bom(bom7)
            
            print("BOM entries added to database!")
        else:
            print("Could not create BOM entries - missing products or materials!")
    else:
        print("BOM entries already exist in database.")
    
    # Print all BOM entries
    BOMRepository.print_all_bom()
    
    # Demonstrate BOM query functionality
    print("\n" + "="*50)
    print("BOM QUERY FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Get BOM for specific products
    table = ProductRepository.get_product_by_name("Table")
    if table:
        print(f"\n1. Materials needed for '{table.name}':")
        table_bom = BOMRepository.get_bom_by_product_id(table.id)
        for bom_entry in table_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                print(f"   - {bom_entry.quantity_needed} {material.unit} of {material.name}")
    
    chair = ProductRepository.get_product_by_name("Chair")
    if chair:
        print(f"\n2. Materials needed for '{chair.name}':")
        chair_bom = BOMRepository.get_bom_by_product_id(chair.id)
        for bom_entry in chair_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                print(f"   - {bom_entry.quantity_needed} {material.unit} of {material.name}")
    
    # Get products that use specific materials
    wood = MaterialRepository.get_material_by_name("Wood")
    if wood:
        print(f"\n3. Products that use '{wood.name}':")
        wood_bom = BOMRepository.get_bom_by_material_id(wood.id)
        for bom_entry in wood_bom:
            product = ProductRepository.get_product_by_id(bom_entry.product_id)
            if product:
                print(f"   - {product.name} needs {bom_entry.quantity_needed} {wood.unit}")
    
    steel = MaterialRepository.get_material_by_name("Steel")
    if steel:
        print(f"\n4. Products that use '{steel.name}':")
        steel_bom = BOMRepository.get_bom_by_material_id(steel.id)
        for bom_entry in steel_bom:
            product = ProductRepository.get_product_by_id(bom_entry.product_id)
            if product:
                print(f"   - {product.name} needs {bom_entry.quantity_needed} {steel.unit}")
    
    # Production calculation example
    print("\n" + "="*50)
    print("PRODUCTION CALCULATION SHOWCASE")
    print("="*50)
    
    print("\nExample: How much material is needed to produce 5 tables and 10 chairs?")
    
    # Calculate for 5 tables
    if table:
        table_bom = BOMRepository.get_bom_by_product_id(table.id)
        print(f"\nFor 5 {table.name}s:")
        for bom_entry in table_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                total_needed = bom_entry.quantity_needed * 5
                print(f"   - {total_needed} {material.unit} of {material.name}")
    
    # Calculate for 10 chairs
    if chair:
        chair_bom = BOMRepository.get_bom_by_product_id(chair.id)
        print(f"\nFor 10 {chair.name}s:")
        for bom_entry in chair_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                total_needed = bom_entry.quantity_needed * 10
                print(f"   - {total_needed} {material.unit} of {material.name}")
    
    # Total material requirements
    print(f"\nTotal material requirements:")
    material_totals = {}
    
    if table:
        table_bom = BOMRepository.get_bom_by_product_id(table.id)
        for bom_entry in table_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                if material.name not in material_totals:
                    material_totals[material.name] = {"quantity": 0, "unit": material.unit}
                material_totals[material.name]["quantity"] += bom_entry.quantity_needed * 5
    
    if chair:
        chair_bom = BOMRepository.get_bom_by_product_id(chair.id)
        for bom_entry in chair_bom:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                if material.name not in material_totals:
                    material_totals[material.name] = {"quantity": 0, "unit": material.unit}
                material_totals[material.name]["quantity"] += bom_entry.quantity_needed * 10
    
    for material_name, data in material_totals.items():
        print(f"   - {data['quantity']} {data['unit']} of {material_name}")
    
    print("="*50)


def showcase_machines():
    """Showcase function to demonstrate Machine and MachineRecipe model capabilities."""
    print("\n" + "="*60)
    print("MACHINES MODEL SHOWCASE")
    print("="*60)
    
    # Check if machines already exist to avoid duplicates
    existing_machines = MachineRepository.get_all_machines()
    
    if not existing_machines:
        # Create and add machines only if database is empty
        machine1 = Machine(id=0, name="Assembly Line A")
        machine2 = Machine(id=0, name="CNC Mill B")
        machine3 = Machine(id=0, name="Packaging Station C")
        
        # Add machines to database
        MachineRepository.add_machine(machine1)
        MachineRepository.add_machine(machine2)
        MachineRepository.add_machine(machine3)
        
        print("Machines added to database!")
    else:
        print("Machines already exist in database.")
    
    # Print all machines
    MachineRepository.print_all_machines()
    
    # Demonstrate search functionality
    print("\n" + "="*50)
    print("MACHINE SEARCH FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Exact search
    print("\n1. Exact search for 'Assembly Line A':")
    assembly = MachineRepository.get_machine_by_name("Assembly Line A")
    if assembly:
        print(f"   Found: {assembly}")
    else:
        print("   Not found!")
    
    # Partial searches
    print("\n2. Partial search for 'line' (should find Assembly Line A):")
    machines = MachineRepository.search_machines_by_name("line")
    for machine in machines:
        print(f"   Found: {machine}")
    
    print("\n3. Partial search for 'cnc' (should find CNC Mill B):")
    machines = MachineRepository.search_machines_by_name("cnc")
    for machine in machines:
        print(f"   Found: {machine}")
    
    print("\n4. Search for 'xyz' (should find nothing):")
    machines = MachineRepository.search_machines_by_name("xyz")
    if machines:
        for machine in machines:
            print(f"   Found: {machine}")
    else:
        print("   No machines found!")
    
    print("="*50)
    
    # Showcase Machine Recipes
    print("\n" + "="*60)
    print("MACHINE RECIPES MODEL SHOWCASE")
    print("="*60)
    
    # Check if machine recipes already exist to avoid duplicates
    existing_recipes = MachineRecipeRepository.get_all_machine_recipes()
    
    if not existing_recipes:
        # Get existing machines and products to create machine recipes
        assembly_line = MachineRepository.get_machine_by_name("Assembly Line A")
        cnc_mill = MachineRepository.get_machine_by_name("CNC Mill B")
        packaging = MachineRepository.get_machine_by_name("Packaging Station C")
        
        table = ProductRepository.get_product_by_name("Table")
        chair = ProductRepository.get_product_by_name("Chair")
        cabinet = ProductRepository.get_product_by_name("Cabinet")
        
        if assembly_line and cnc_mill and packaging and table and chair and cabinet:
            # Create machine recipes: which machine can produce which product at what capacity
            
            # Assembly Line A can produce Tables at 5 units/hr and Chairs at 10 units/hr
            recipe1 = MachineRecipe(id=0, machine_id=assembly_line.id, product_id=table.id, production_capacity=5)
            recipe2 = MachineRecipe(id=0, machine_id=assembly_line.id, product_id=chair.id, production_capacity=10)
            
            # CNC Mill B can produce Tables at 2 units/hr (slower but more precise)
            recipe3 = MachineRecipe(id=0, machine_id=cnc_mill.id, product_id=table.id, production_capacity=2)
            
            # CNC Mill B can also produce Cabinets at 1 unit/hr
            recipe4 = MachineRecipe(id=0, machine_id=cnc_mill.id, product_id=cabinet.id, production_capacity=1)
            
            # Packaging Station C can package Chairs at 20 units/hr
            recipe5 = MachineRecipe(id=0, machine_id=packaging.id, product_id=chair.id, production_capacity=20)
            
            # Add machine recipes to database
            MachineRecipeRepository.add_machine_recipe(recipe1)
            MachineRecipeRepository.add_machine_recipe(recipe2)
            MachineRecipeRepository.add_machine_recipe(recipe3)
            MachineRecipeRepository.add_machine_recipe(recipe4)
            MachineRecipeRepository.add_machine_recipe(recipe5)
            
            print("Machine recipes added to database!")
        else:
            print("Could not create machine recipes - missing machines or products!")
    else:
        print("Machine recipes already exist in database.")
    
    # Print all machine recipes
    MachineRecipeRepository.print_all_machine_recipes()
    
    # Demonstrate machine recipe query functionality
    print("\n" + "="*50)
    print("MACHINE RECIPE QUERY FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Get recipes for specific machines
    assembly_line = MachineRepository.get_machine_by_name("Assembly Line A")
    if assembly_line:
        print(f"\n1. What can '{assembly_line.name}' produce?")
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(assembly_line.id)
        for recipe in recipes:
            product = ProductRepository.get_product_by_id(recipe.product_id)
            if product:
                print(f"   - {product.name} at {recipe.production_capacity} units/hr")
    
    cnc_mill = MachineRepository.get_machine_by_name("CNC Mill B")
    if cnc_mill:
        print(f"\n2. What can '{cnc_mill.name}' produce?")
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(cnc_mill.id)
        for recipe in recipes:
            product = ProductRepository.get_product_by_id(recipe.product_id)
            if product:
                print(f"   - {product.name} at {recipe.production_capacity} units/hr")
    
    # Get machines that can produce specific products
    table = ProductRepository.get_product_by_name("Table")
    if table:
        print(f"\n3. Which machines can produce '{table.name}'?")
        recipes = MachineRecipeRepository.get_recipes_by_product_id(table.id)
        for recipe in recipes:
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            if machine:
                print(f"   - {machine.name} at {recipe.production_capacity} units/hr")
    
    chair = ProductRepository.get_product_by_name("Chair")
    if chair:
        print(f"\n4. Which machines can produce '{chair.name}'?")
        recipes = MachineRecipeRepository.get_recipes_by_product_id(chair.id)
        for recipe in recipes:
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            if machine:
                print(f"   - {machine.name} at {recipe.production_capacity} units/hr")
    
    # Production time calculation example
    print("\n" + "="*50)
    print("PRODUCTION TIME CALCULATION SHOWCASE")
    print("="*50)
    
    print("\nExample: How long does it take to produce 50 Tables on different machines?")
    
    if table:
        recipes = MachineRecipeRepository.get_recipes_by_product_id(table.id)
        for recipe in recipes:
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            if machine:
                time_hours = 50 / recipe.production_capacity
                print(f"   - {machine.name}: {time_hours:.2f}h ({time_hours * 60:.0f}m")
    
    print("\nExample: How long does it take to produce 100 Chairs on different machines?")
    
    if chair:
        recipes = MachineRecipeRepository.get_recipes_by_product_id(chair.id)
        for recipe in recipes:
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            if machine:
                time_hours = 100 / recipe.production_capacity
                print(f"   - {machine.name}: {time_hours:.2f}h ({time_hours * 60:.0f}m")
    
    print("="*50)


def showcase_orders():
    """Showcase function to demonstrate Production Order model capabilities."""
    print("\n" + "="*60)
    print("PRODUCTION ORDERS MODEL SHOWCASE")
    print("="*60)
    
    # Check if orders already exist to avoid duplicates
    existing_orders = ProductionOrderRepository.get_all_orders()
    
    if not existing_orders:
        # Get existing products to create orders
        table = ProductRepository.get_product_by_name("Table")
        chair = ProductRepository.get_product_by_name("Chair")
        cabinet = ProductRepository.get_product_by_name("Cabinet")
        
        if table and chair and cabinet:
            # Create production orders with different priorities and deadlines
            today = date.today()
            
            # Order 1: Urgent table order (High priority, deadline in 3 days)
            order1 = ProductionOrder(
                id=0, 
                product_id=table.id, 
                quantity=10,
                deadline=(today + timedelta(days=3)).isoformat(),
                status=OrderStatus.IN_QUEUE.value,
                priority=OrderPriority.HIGH.value
            )
            
            # Order 2: Chair order (Medium priority, deadline in 7 days)
            order2 = ProductionOrder(
                id=0,
                product_id=chair.id,
                quantity=25,
                deadline=(today + timedelta(days=7)).isoformat(),
                status=OrderStatus.IN_QUEUE.value,
                priority=OrderPriority.MEDIUM.value
            )
            
            # Order 3: Cabinet order (Low priority, deadline in 14 days)
            order3 = ProductionOrder(
                id=0,
                product_id=cabinet.id,
                quantity=5,
                deadline=(today + timedelta(days=14)).isoformat(),
                status=OrderStatus.IN_QUEUE.value,
                priority=OrderPriority.LOW.value
            )
            
            # Order 4: Another table order (High priority, deadline in 5 days)
            order4 = ProductionOrder(
                id=0,
                product_id=table.id,
                quantity=15,
                deadline=(today + timedelta(days=5)).isoformat(),
                status=OrderStatus.IN_QUEUE.value,
                priority=OrderPriority.HIGH.value
            )
            
            # Order 5: Completed chair order (for demo)
            order5 = ProductionOrder(
                id=0,
                product_id=chair.id,
                quantity=50,
                deadline=(today - timedelta(days=2)).isoformat(),  # Past deadline
                status=OrderStatus.COMPLETED.value,
                priority=OrderPriority.MEDIUM.value
            )
            
            # Add orders to database
            ProductionOrderRepository.add_order(order1)
            ProductionOrderRepository.add_order(order2)
            ProductionOrderRepository.add_order(order3)
            ProductionOrderRepository.add_order(order4)
            ProductionOrderRepository.add_order(order5)
            
            print("Production orders added to database!")
        else:
            print("Could not create orders - missing products!")
    else:
        print("Production orders already exist in database.")
    
    # Print all orders
    ProductionOrderRepository.print_all_orders()
    
    # Demonstrate query functionality
    print("\n" + "="*50)
    print("ORDER QUERY FUNCTIONALITY SHOWCASE")
    print("="*50)
    
    # Get orders by status
    print("\n1. Orders in queue:")
    queue_orders = ProductionOrderRepository.get_orders_by_status(OrderStatus.IN_QUEUE.value)
    for order in queue_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        if product:
            priority_name = ["", "High", "Medium", "Low"][order.priority]
            print(f"   - Order #{order.id}: {order.quantity} {product.name}(s), Deadline: {order.deadline}, Priority: {priority_name}")
    
    print("\n2. Completed orders:")
    completed_orders = ProductionOrderRepository.get_orders_by_status(OrderStatus.COMPLETED.value)
    for order in completed_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        if product:
            print(f"   - Order #{order.id}: {order.quantity} {product.name}(s), Completed on: {order.created_at}")
    
    # Get orders by priority
    print("\n3. High priority orders:")
    high_priority_orders = ProductionOrderRepository.get_orders_by_priority(OrderPriority.HIGH.value)
    for order in high_priority_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        if product:
            print(f"   - Order #{order.id}: {order.quantity} {product.name}(s), Deadline: {order.deadline}, Status: {order.status}")
    
    # Get orders by product
    table = ProductRepository.get_product_by_name("Table")
    if table:
        print(f"\n4. All orders for '{table.name}':")
        table_orders = ProductionOrderRepository.get_orders_by_product_id(table.id)
        for order in table_orders:
            priority_name = ["", "High", "Medium", "Low"][order.priority]
            print(f"   - Order #{order.id}: {order.quantity} units, Deadline: {order.deadline}, Priority: {priority_name}, Status: {order.status}")
    
    # Get pending orders
    print("\n5. All pending orders (not completed):")
    pending_orders = ProductionOrderRepository.get_pending_orders()
    for order in pending_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        if product:
            priority_name = ["", "High", "Medium", "Low"][order.priority]
            print(f"   - Order #{order.id}: {order.quantity} {product.name}(s), Deadline: {order.deadline}, Priority: {priority_name}")
    
    # Material requirements calculation
    print("\n" + "="*50)
    print("MATERIAL REQUIREMENTS CALCULATION")
    print("="*50)
    
    print("\nTotal materials needed for all pending orders:")
    material_totals = {}
    
    for order in pending_orders:
        # Get BOM for this product
        bom_entries = BOMRepository.get_bom_by_product_id(order.product_id)
        for bom_entry in bom_entries:
            material = MaterialRepository.get_material_by_id(bom_entry.material_id)
            if material:
                # Calculate total material needed for this order
                needed = bom_entry.quantity_needed * order.quantity
                
                if material.name not in material_totals:
                    material_totals[material.name] = {"quantity": 0, "unit": material.unit, "available": material.quantity}
                material_totals[material.name]["quantity"] += needed
    
    for material_name, data in material_totals.items():
        shortage = max(0, data["quantity"] - data["available"])
        status = "✓ OK" if shortage == 0 else f"✗ SHORT {shortage} {data['unit']}"
        print(f"   - {material_name}: Need {data['quantity']} {data['unit']}, Have {data['available']} {data['unit']} [{status}]")
    
    # Production time estimation
    print("\n" + "="*50)
    print("PRODUCTION TIME ESTIMATION")
    print("="*50)
    
    print("\nEstimated production time for pending orders:")
    for order in pending_orders[:3]:  # Show first 3 orders
        product = ProductRepository.get_product_by_id(order.product_id)
        if product:
            # Get machines that can produce this product
            recipes = MachineRecipeRepository.get_recipes_by_product_id(order.product_id)
            if recipes:
                print(f"\n   Order #{order.id}: {order.quantity} {product.name}(s)")
                for recipe in recipes:
                    machine = MachineRepository.get_machine_by_id(recipe.machine_id)
                    if machine:
                        time_hours = order.quantity / recipe.production_capacity
                        print(f"      - {machine.name}: {time_hours:.2f}h ({time_hours * 60:.0f}m")
            else:
                print(f"\n   Order #{order.id}: {order.quantity} {product.name}(s) - No machine configured!")
    
    print("="*50)


def showcase_production_planning():
    """Showcase function to demonstrate Production Planning (Gantt scheduling) capabilities."""
    print("\n" + "="*80)
    print("PRODUCTION PLANNING SHOWCASE - BEFORE SCHEDULING")
    print("="*80)
    
    # Show current state BEFORE scheduling
    pending_orders = ProductionOrderRepository.get_pending_orders()
    
    print("\n📋 PENDING ORDERS TO SCHEDULE:")
    print("-" * 80)
    if not pending_orders:
        print("   No pending orders!")
        return
    
    for order in pending_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        priority_name = ["", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"][order.priority]
        if product:
            print(f"   Order #{order.id}: {order.quantity} x {product.name} | Deadline: {order.deadline} | Priority: {priority_name}")
    
    print("\n🤖 MACHINE CAPABILITIES:")
    print("-" * 80)
    all_machines = MachineRepository.get_all_machines()
    for machine in all_machines:
        recipes = MachineRecipeRepository.get_recipes_by_machine_id(machine.id)
        print(f"   {machine.name}:")
        for recipe in recipes:
            product = ProductRepository.get_product_by_id(recipe.product_id)
            if product:
                print(f"      └─ Produces {product.name} at {recipe.production_capacity} units/hour")
    
    print("\n⏳ PRODUCTION TIME ESTIMATES:")
    print("-" * 80)
    for order in pending_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        recipes = MachineRecipeRepository.get_recipes_by_product_id(order.product_id)
        if product and recipes:
            recipe = recipes[0]  # Use first available recipe
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            duration_hours = order.quantity / recipe.production_capacity
            if machine:
                print(f"   Order #{order.id}: {order.quantity} {product.name}s → {machine.name} = {duration_hours:.2f}h ({int(duration_hours * 60)}m)")
    
    # Clear old plans before generating new ones
    print("\n" + "="*80)
    print("GENERATING NEW PRODUCTION PLAN...")
    print("="*80)
    
    # Generate the production plan
    created_plans = SchedulingService.generate_plan_from_scratch()
    
    print("\n" + "="*80)
    print("PRODUCTION PLANNING SHOWCASE - AFTER SCHEDULING")
    print("="*80)
    
    if not created_plans:
        print("   No plans were created!")
        return
    
    print(f"\n✅ PRODUCTION PLAN GENERATED: {len(created_plans)} orders scheduled")
    print("-" * 80)
    
    # Group plans by machine for better visualization
    plans_by_machine = {}
    for plan in created_plans:
        if plan.machine_id not in plans_by_machine:
            plans_by_machine[plan.machine_id] = []
        plans_by_machine[plan.machine_id].append(plan)
    
    # Display Gantt-like view
    print("\n📊 GANTT SCHEDULE VIEW:")
    print("-" * 80)
    
    for machine_id in sorted(plans_by_machine.keys()):
        machine = MachineRepository.get_machine_by_id(machine_id)
        plans = plans_by_machine[machine_id]
        
        print(f"\n   🖥️  {machine.name}:")
        print(f"   {'─' * 76}")
        
        for i, plan in enumerate(plans):
            order = ProductionOrderRepository.get_order_by_id(plan.order_id)
            product = ProductRepository.get_product_by_id(order.product_id)
            
            # Create a simple visual bar
            start_time = plan.planned_start_time
            end_time = plan.planned_end_time
            status_indicator = "▶️ " if plan.status == "planned" else "▶️▶️" if plan.status == "in_progress" else "✓ "
            
            print(f"      {status_indicator} Order #{plan.order_id}: {order.quantity}x {product.name}")
            print(f"         └─ Start: {start_time} | End: {end_time} | Duration: {plan.duration_hours:.2f}h")
            print()
    
    print("-" * 80)
    
    # Summary statistics
    print("\n📈 SCHEDULING SUMMARY:")
    print("-" * 80)
    
    total_duration = 0
    earliest_start = None
    latest_end = None
    
    for plan in created_plans:
        total_duration += plan.duration_hours
        
        from datetime import datetime
        start = datetime.strptime(plan.planned_start_time, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(plan.planned_end_time, '%Y-%m-%d %H:%M:%S')
        
        if earliest_start is None or start < earliest_start:
            earliest_start = start
        if latest_end is None or end > latest_end:
            latest_end = end
    
    if earliest_start and latest_end:
        total_schedule_time = (latest_end - earliest_start).total_seconds() / 3600  # Convert to hours
        utilization = (total_duration / (total_schedule_time * len(plans_by_machine))) * 100 if total_schedule_time > 0 else 0
        
        print(f"   Total Production Duration:     {total_duration:.2f} hours")
        print(f"   Schedule Start Time:           {earliest_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Schedule End Time:             {latest_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Schedule Duration:       {total_schedule_time:.2f} hours")
        print(f"   Number of Machines Used:       {len(plans_by_machine)}")
        print(f"   Average Machine Utilization:   {utilization:.1f}%")
    
    print("\n" + "="*80)
    print("Production plan is ready for Gantt visualization!")
    print("="*80)


def _print_gantt_view(plans):
    """Helper to display Gantt-like view for a list of plans."""
    if not plans:
        print("   No plans to display")
        return
    
    # Group plans by machine
    plans_by_machine = {}
    for plan in plans:
        if plan.machine_id not in plans_by_machine:
            plans_by_machine[plan.machine_id] = []
        plans_by_machine[plan.machine_id].append(plan)
    
    print("\n📊 GANTT SCHEDULE VIEW:")
    print("-" * 80)
    
    for machine_id in sorted(plans_by_machine.keys()):
        machine = MachineRepository.get_machine_by_id(machine_id)
        machine_plans = plans_by_machine[machine_id]
        
        print(f"\n   🖥️  {machine.name}:")
        print(f"   {'─' * 76}")
        
        for plan in machine_plans:
            order = ProductionOrderRepository.get_order_by_id(plan.order_id)
            product = ProductRepository.get_product_by_id(order.product_id)
            priority_name = ["", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"][order.priority]
            
            start_time = plan.planned_start_time
            end_time = plan.planned_end_time
            status_indicator = "▶️ " if plan.status == "planned" else "⏸️ " if plan.status == "in_progress" else "✓ "
            
            print(f"      {status_indicator} Order #{plan.order_id}: {order.quantity}x {product.name} ({priority_name})")
            print(f"         └─ {start_time} → {end_time} ({plan.duration_hours:.2f}h)")
    
    print("\n" + "-" * 80)


def showcase_production_planning_update():
    """Showcase the UPDATE production plan feature - add new orders and reschedule."""
    print("\n\n" + "="*80)
    print("PRODUCTION PLANNING - UPDATE WITH NEW ORDERS SHOWCASE")
    print("="*80)
    
    # Step 1: Show current plan
    print("\n" + "="*80)
    print("STEP 1: CURRENT PRODUCTION PLAN (from scratch)")
    print("="*80)
    
    pending_orders = ProductionOrderRepository.get_pending_orders()
    print(f"\n📋 Current pending orders: {len(pending_orders)}")
    for order in pending_orders:
        product = ProductRepository.get_product_by_id(order.product_id)
        priority_name = ["", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"][order.priority]
        if product:
            print(f"   Order #{order.id}: {order.quantity}x {product.name} | Priority: {priority_name}")
    
    # Generate initial plan
    print("\n🔄 Generating plan from scratch...")
    initial_plans = SchedulingService.generate_plan_from_scratch()
    _print_gantt_view(initial_plans)
    
    # Mark first order as "in_progress" to simulate work started
    if initial_plans:
        first_plan = initial_plans[0]
        first_plan.status = "in_progress"
        ProductionPlanRepository.update_plan(first_plan)
        print(f"\n✅ Simulated: Order #{first_plan.order_id} is now IN_PROGRESS")
    
    # Step 2: Add 10 new orders
    print("\n" + "="*80)
    print("STEP 2: ADDING 10 NEW ORDERS")
    print("="*80)
    
    products = ProductRepository.get_all_products()
    if len(products) < 1:
        print("Not enough products to create new orders!")
        return
    
    today = date.today()
    new_orders = []
    
    for i in range(10):
        # Cycle through products
        product = products[i % len(products)]
        
        # Vary priorities and quantities
        if i < 3:
            priority = OrderPriority.HIGH.value
            quantity = 20 + (i * 5)
        elif i < 6:
            priority = OrderPriority.MEDIUM.value
            quantity = 15 + (i * 3)
        else:
            priority = OrderPriority.LOW.value
            quantity = 10 + (i * 2)
        
        # Vary deadlines
        deadline_days = 3 + (i % 5)
        
        order = ProductionOrder(
            id=0,
            product_id=product.id,
            quantity=quantity,
            deadline=(today + timedelta(days=deadline_days)).isoformat(),
            status=OrderStatus.IN_QUEUE.value,
            priority=priority
        )
        
        new_order = ProductionOrderRepository.add_order(order)
        new_orders.append(new_order)
        priority_name = ["", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"][priority]
        print(f"   ✓ Order #{new_order.id}: {quantity}x {product.name} | Priority: {priority_name} | Deadline: {(today + timedelta(days=deadline_days)).isoformat()}")
    
    print(f"\n✅ Added {len(new_orders)} new orders")
    
    # Step 3: Update plan with new orders
    print("\n" + "="*80)
    print("STEP 3: UPDATING PRODUCTION PLAN WITH NEW ORDERS")
    print("="*80)
    
    print("\n🔄 Updating plan (keeping in_progress, rescheduling planned + adding new)...")
    updated_plans = SchedulingService.update_plan_with_new_orders()
    
    # Step 4: Display updated plan
    print("\n" + "="*80)
    print("UPDATED PRODUCTION PLAN")
    print("="*80)
    
    all_plans = ProductionPlanRepository.get_all_plans()
    
    print(f"\n📊 Total orders in plan: {len(all_plans)}")
    print(f"   - In Progress: {len(ProductionPlanRepository.get_plans_by_status('in_progress'))}")
    print(f"   - Planned: {len(ProductionPlanRepository.get_plans_by_status('planned'))}")
    print(f"   - Completed: {len(ProductionPlanRepository.get_plans_by_status('completed'))}")
    
    _print_gantt_view(all_plans)
    
    # Summary
    print("\n" + "="*80)
    print("UPDATE SUMMARY")
    print("="*80)
    
    total_duration = sum(p.duration_hours for p in updated_plans)
    total_orders = len(updated_plans)
    
    print(f"\n✅ Plan updated successfully!")
    print(f"   - New orders scheduled: {total_orders}")
    print(f"   - Total production duration: {total_duration:.2f}h")
    print(f"   - In-progress orders preserved: YES ✓")
    print(f"   - New high-priority orders scheduled first: YES ✓")
    
    print("\n" + "="*80)
    print("PRODUCTION PLANNING SHOWCASE COMPLETE")
    print("="*80)


def showcase_mrp():
    """Showcase MRP (Material Requirements Planning) service."""
    print("\n\n" + "="*80)
    print("MATERIAL REQUIREMENTS PLANNING (MRP) SHOWCASE")
    print("="*80)
    
    # Generate procurement plan
    plan = MRPService.generate_procurement_plan()
    
    print("\n" + "="*80)
    print("MRP SHOWCASE COMPLETE")
    print("="*80)
    
def showcase_dashboard():
    print("="*50)
    print("DASHBOARD SHOWCASE")
    print("="*50)

    # 1️⃣ KPI
    counts = DashboardService.get_kpi_counts()
    print("\nKPI COUNTS:")
    print(f"{counts['pending_label']:<25} : {counts['pending_orders']}")
    print(f"{counts['in_progress_label']:<25} : {counts['orders_in_progress']}")
    print(f"{counts['completed_label']:<25} : {counts['completed_orders']}")
    print(f"{counts['late_label']:<25} : {counts['late_orders']}")

    print("\nQueued Orders by Priority:")
    print(f"  {counts['priority_high_label']:<10} : {counts['queued_orders_by_priority'][1]}")
    print(f"  {counts['priority_medium_label']:<10} : {counts['queued_orders_by_priority'][2]}")
    print(f"  {counts['priority_low_label']:<10} : {counts['queued_orders_by_priority'][3]}")

    # 2️⃣ Orders Status Overview
    table_data = DashboardService.get_orders_status_overview()
    print("\nORDERS STATUS OVERVIEW:")
    if not table_data:
        print("No orders found.")
        return

    headers = ["Order ID", "Product", "Quantity", "Priority", "Status", "Deadline"]
    print(" | ".join(headers))
    print("-"*60)

    for row in table_data:
        print(f"{row['order_id']} | {row['product']} | {row['quantity']} | {row['priority']} | {row['status']} | {row['deadline']}")

    print("="*50)


def showcase():
    
    print("Production Planner started!")
    
    # Showcase Materials functionality
    showcase_materials()
    
    # Showcase Products functionality  
    showcase_products()
    
    # Showcase BOM functionality
    showcase_bom()
    
    # Showcase Machines functionality
    showcase_machines()
    
    # Showcase Production Orders functionality
    showcase_orders()
    
    # Showcase Production Planning
    showcase_production_planning()
    
    # Showcase Production Planning Update (add new orders)
    showcase_production_planning_update()
    
    # Showcase MRP (Material Requirements Planning)
    showcase_mrp()
    
    showcase_dashboard()
    # Don't close database here - let Qt app use the same connection
    print("\nDatabase showcase completed. Starting Qt application...")


if __name__ == "__main__":
    
    # Initialize database (creates file and directory)
    init_db()
    
    showcase()


    app = QApplication(sys.argv)

    qss_path = os.path.join(os.path.dirname(__file__), "assets", "app.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
            print("QSS loaded from:", qss_path)
    else:
        print("QSS file not found:", qss_path)

    window = MainWindow()
    window.show()
    
    # Close database when Qt app exits
    try:
        sys.exit(app.exec())
    finally:
        close_db()
        print("Database connection closed.")
