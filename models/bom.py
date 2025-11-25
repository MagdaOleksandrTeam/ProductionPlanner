from . import database
from dataclasses import dataclass
from typing import List

@dataclass
class BOM():
    id: int
    product_id: int
    material_id: int
    quantity_needed: float
    
    def __str__(self) -> str:
        return f"BOM(ID: {self.id}, Product ID: {self.product_id}, Material ID: {self.material_id}, Quantity: {self.quantity_needed})"
    
    
class BOMRepository:
    @staticmethod
    def init_table():
        """Creates the bom table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bom (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    quantity_needed REAL NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE,
                    UNIQUE(product_id, material_id)
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_bom(bom: BOM):
        """Adds a new BOM entry to the database. Returns the BOM with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bom (product_id, material_id, quantity_needed) 
                VALUES (?, ?, ?)
            """, (bom.product_id, bom.material_id, bom.quantity_needed))
            conn.commit()
            bom.id = cursor.lastrowid
        return bom

    @staticmethod
    def get_bom_by_id(bom_id: int) -> BOM:
        """Fetches a BOM entry by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, product_id, material_id, quantity_needed FROM bom WHERE id = ?", (bom_id,))
            row = cursor.fetchone()
            if row:
                return BOM(id=row[0], product_id=row[1], material_id=row[2], quantity_needed=row[3])
            return None
        
    @staticmethod
    def get_bom_by_product_id(product_id: int) -> List[BOM]:
        """Fetches all BOM entries for a specific product."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, product_id, material_id, quantity_needed FROM bom WHERE product_id = ?", (product_id,))
            rows = cursor.fetchall()
            return [BOM(id=row[0], product_id=row[1], material_id=row[2], quantity_needed=row[3]) for row in rows]
    
    @staticmethod
    def get_bom_by_material_id(material_id: int) -> List[BOM]:
        """Fetches all BOM entries that use a specific material."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, product_id, material_id, quantity_needed FROM bom WHERE material_id = ?", (material_id,))
            rows = cursor.fetchall()
            return [BOM(id=row[0], product_id=row[1], material_id=row[2], quantity_needed=row[3]) for row in rows]
        
    @staticmethod
    def update_bom(bom: BOM):
        """Updates an existing BOM entry in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bom 
                SET product_id = ?, material_id = ?, quantity_needed = ? 
                WHERE id = ?
            """, (bom.product_id, bom.material_id, bom.quantity_needed, bom.id))
            conn.commit()

    @staticmethod
    def delete_bom(bom: BOM):
        """Deletes a BOM entry from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bom WHERE id = ?", (bom.id,))
            conn.commit()
    
    @staticmethod
    def get_all_bom() -> List[BOM]:
        """Returns all BOM entries from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, product_id, material_id, quantity_needed FROM bom ORDER BY id")
            rows = cursor.fetchall()
            return [BOM(id=row[0], product_id=row[1], material_id=row[2], quantity_needed=row[3]) for row in rows]
    
    @staticmethod
    def print_all_bom():
        """Prints all BOM entries in a formatted way. Just for demo purposes."""
        boms = BOMRepository.get_all_bom()
        if not boms:
            print("No BOM entries found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"{'BOM LIST':^60}")
        print(f"{'='*60}")
        for bom in boms:
            print(bom)
        print(f"{'='*60}")
        print(f"Total BOM entries: {len(boms)}")
        print()