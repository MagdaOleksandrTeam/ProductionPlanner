import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from models.database import init_db, close_db, get_connection
from models.material import Material, MaterialRepository
from models.product import Product, ProductRepository

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


def showcase():
    
    # Initialize database (creates file and directory)
    init_db()
    
    print("Production Planner started!")
    
    # Showcase Materials functionality
    showcase_materials()
    
    # Showcase Products functionality  
    showcase_products()
    
    # Don't close database here - let Qt app use the same connection
    print("\nDatabase showcase completed. Starting Qt application...")


if __name__ == "__main__":
    showcase()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Close database when Qt app exits
    try:
        sys.exit(app.exec())
    finally:
        close_db()
        print("Database connection closed.")
