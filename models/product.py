from . import database
from dataclasses import dataclass
from typing import List

@dataclass
class Product():
    id: int
    name: str
    unit: str
    description: str = ""
    quantity: float = 0.0
    
    def __str__(self) -> str:
        return f"Product(ID: {self.id}, Name: '{self.name}', Quantity: {self.quantity} {self.unit}, Description: '{self.description}')"
    
    
class ProductRepository:
    @staticmethod
    def init_table():
        """Creates the products table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    unit TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    quantity REAL DEFAULT 0
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_product(product: Product):
        """Adds a new product to the database. Returns the product with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, unit, description, quantity) 
                VALUES (?, ?, ?, 0)
            """, (product.name, product.unit, product.description))
            conn.commit()
            product.id = cursor.lastrowid
            product.quantity = 0.0  # Ensure quantity is set to 0 for new products
        return product

    @staticmethod
    def get_product_by_id(product_id: int) -> Product:
        """Fetches a product by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, unit, description, quantity FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(id=row[0], name=row[1], unit=row[2], description=row[3], quantity=row[4])
            return None
        
    @staticmethod
    def get_product_by_name(product_name: str) -> Product:
        """Fetches a product by its exact name. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, unit, description, quantity FROM products WHERE name = ?", (product_name,))
            row = cursor.fetchone()
            if row:
                return Product(id=row[0], name=row[1], unit=row[2], description=row[3], quantity=row[4])
            return None
    
    @staticmethod
    def search_products_by_name(partial_name: str) -> List[Product]:
        """Searches for products containing the partial name. Case-insensitive."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            # Use LIKE with % wildcards for partial matching, LOWER() for case-insensitive
            cursor.execute("""
                SELECT id, name, unit, description, quantity 
                FROM products 
                WHERE LOWER(name) LIKE LOWER(?) 
                ORDER BY name
            """, (f"%{partial_name}%",))
            rows = cursor.fetchall()
            return [Product(id=row[0], name=row[1], unit=row[2], description=row[3], quantity=row[4]) for row in rows]
        
    @staticmethod
    def update_product(product: Product):
        """Updates an existing product in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name = ?, unit = ?, description = ?, quantity = ? 
                WHERE id = ?
            """, (product.name, product.unit, product.description, product.quantity, product.id))
            conn.commit()

    @staticmethod
    def delete_product(product: Product):
        """Deletes a product from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product.id,))
            conn.commit()
    
    @staticmethod
    def get_all_products() -> List[Product]:
        """Returns all products from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, unit, description, quantity FROM products ORDER BY id")
            rows = cursor.fetchall()
            return [Product(id=row[0], name=row[1], unit=row[2], description=row[3], quantity=row[4]) for row in rows]
    
    @staticmethod
    def print_all_products():
        """Prints all products in a formatted way. Just for demo purposes."""
        products = ProductRepository.get_all_products()
        if not products:
            print("No products found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"{'PRODUCTS LIST':^60}")
        print(f"{'='*60}")
        for product in products:
            print(product)
        print(f"{'='*60}")
        print(f"Total products: {len(products)}")
        print()