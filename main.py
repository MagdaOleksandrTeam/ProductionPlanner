import sys, os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from models.database import init_db, close_db, get_connection
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository
from models.bom import BOM, BOMRepository

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
