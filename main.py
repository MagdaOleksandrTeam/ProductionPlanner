import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from models.database import init_db, close_db, get_connection
from models.material import Material, MaterialRepository

def main():
    
    # Initialize database (creates file and directory)
    init_db()
    
    print("Production Planner started!")
    
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
    print("\n" + "="*60)
    print("SEARCH FUNCTIONALITY DEMO")
    print("="*60)
    
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
    
    print("="*60)
    
    # Close the shared connection
    close_db()
    

if __name__ == "__main__":
    main()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
