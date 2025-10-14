from . import database
from dataclasses import dataclass
from typing import List

@dataclass
class Material():
    id: int
    name: str
    quantity: float
    unit: str
    
    def __str__(self) -> str:
        return f"Material(ID: {self.id}, Name: '{self.name}', Quantity: {self.quantity} {self.unit})"
    
    
class MaterialRepository:
    @staticmethod
    def init_table():
        """Creates the materials table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    unit TEXT NOT NULL,
                    quantity REAL DEFAULT 0
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_material(material: Material):
        """Adds a new material to the database. Returns the material with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO materials (name, unit, quantity) 
                VALUES (?, ?, ?)
            """, (material.name, material.unit, material.quantity))
            conn.commit()
            material.id = cursor.lastrowid
        return material

    @staticmethod
    def get_material_by_id(material_id: int) -> Material:
        """Fetches a material by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, unit, quantity FROM materials WHERE id = ?", (material_id,))
            row = cursor.fetchone()
            if row:
                return Material(id=row[0], name=row[1], unit=row[2], quantity=row[3])
            return None
        
    @staticmethod
    def get_material_by_name(material_name: str) -> Material:
        """Fetches a material by its exact name. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, unit, quantity FROM materials WHERE name = ?", (material_name,))
            row = cursor.fetchone()
            if row:
                return Material(id=row[0], name=row[1], unit=row[2], quantity=row[3])
            return None
    
    @staticmethod
    def search_materials_by_name(partial_name: str) -> List[Material]:
        """Searches for materials containing the partial name. Case-insensitive."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            # Use LIKE with % wildcards for partial matching, LOWER() for case-insensitive
            cursor.execute("""
                SELECT id, name, unit, quantity 
                FROM materials 
                WHERE LOWER(name) LIKE LOWER(?) 
                ORDER BY name
            """, (f"%{partial_name}%",))
            rows = cursor.fetchall()
            return [Material(id=row[0], name=row[1], unit=row[2], quantity=row[3]) for row in rows]
        
    @staticmethod
    def update_material(material: Material):
        """Updates an existing material in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE materials 
                SET name = ?, unit = ?, quantity = ? 
                WHERE id = ?
            """, (material.name, material.unit, material.quantity, material.id))
            conn.commit()

    @staticmethod
    def delete_material(Material: Material):
        """Deletes a material from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materials WHERE id = ?", (Material.id,))
            conn.commit()
    
    @staticmethod
    def get_all_materials() -> List[Material]:
        """Returns all materials from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, quantity, unit FROM materials ORDER BY id")
            rows = cursor.fetchall()
            return [Material(id=row[0], name=row[1], quantity=row[2], unit=row[3]) for row in rows]
    
    @staticmethod
    def print_all_materials():
        """Prints all materials in a formatted way. Just for demo purposes."""
        materials = MaterialRepository.get_all_materials()
        if not materials:
            print("No materials found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"{'MATERIALS LIST':^60}")
        print(f"{'='*60}")
        for material in materials:
            print(material)
        print(f"{'='*60}")
        print(f"Total materials: {len(materials)}")
        print()