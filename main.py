import sys, os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from models.database import init_db, close_db, get_connection
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM, BOMRepository
from models.machine import Machine, MachineRecipe, MachineRepository, MachineRecipeRepository
from models.order import ProductionOrder, ProductionOrderRepository, OrderStatus, OrderPriority
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
            recipe1 = MachineRecipe(id=0, machine_id=assembly_line.id, product_id=table.id, production_capacity=5.0)
            recipe2 = MachineRecipe(id=0, machine_id=assembly_line.id, product_id=chair.id, production_capacity=10.0)
            
            # CNC Mill B can produce Tables at 2 units/hr (slower but more precise)
            recipe3 = MachineRecipe(id=0, machine_id=cnc_mill.id, product_id=table.id, production_capacity=2.0)
            
            # CNC Mill B can also produce Cabinets at 1.5 units/hr
            recipe4 = MachineRecipe(id=0, machine_id=cnc_mill.id, product_id=cabinet.id, production_capacity=1.5)
            
            # Packaging Station C can package Chairs at 20 units/hr
            recipe5 = MachineRecipe(id=0, machine_id=packaging.id, product_id=chair.id, production_capacity=20.0)
            
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
                print(f"   - {machine.name}: {time_hours:.2f} hours ({time_hours * 60:.0f} minutes)")
    
    print("\nExample: How long does it take to produce 100 Chairs on different machines?")
    
    if chair:
        recipes = MachineRecipeRepository.get_recipes_by_product_id(chair.id)
        for recipe in recipes:
            machine = MachineRepository.get_machine_by_id(recipe.machine_id)
            if machine:
                time_hours = 100 / recipe.production_capacity
                print(f"   - {machine.name}: {time_hours:.2f} hours ({time_hours * 60:.0f} minutes)")
    
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
                        print(f"      - {machine.name}: {time_hours:.2f} hours ({time_hours * 60:.0f} minutes)")
            else:
                print(f"\n   Order #{order.id}: {order.quantity} {product.name}(s) - No machine configured!")
    
    print("="*50)


def showcase():
    
    # Initialize database (creates file and directory)
    init_db()
    
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
    
    # Don't close database here - let Qt app use the same connection
    print("\nDatabase showcase completed. Starting Qt application...")


if __name__ == "__main__":
    showcase()


    app = QApplication(sys.argv)

    qss_path = os.path.join(os.path.dirname(__file__), "styles", "app.qss")
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
