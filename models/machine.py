from . import database
from dataclasses import dataclass
from typing import List

@dataclass
class Machine():
    id: int
    name: str
    
    def __str__(self) -> str:
        return f"Machine(ID: {self.id}, Name: '{self.name}')"
    

@dataclass
class MachineRecipe():
    id: int
    machine_id: int
    product_id: int
    production_capacity: float  # units per hour
    
    def __str__(self) -> str:
        return f"MachineRecipe(ID: {self.id}, Machine ID: {self.machine_id}, Product ID: {self.product_id}, Capacity: {self.production_capacity} units/hr)"


class MachineRepository:
    @staticmethod
    def init_table():
        """Creates the machines table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_machine(machine: Machine):
        """Adds a new machine to the database. Returns the machine with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO machines (name) 
                VALUES (?)
            """, (machine.name,))
            conn.commit()
            machine.id = cursor.lastrowid
        return machine

    @staticmethod
    def get_machine_by_id(machine_id: int) -> Machine:
        """Fetches a machine by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM machines WHERE id = ?", (machine_id,))
            row = cursor.fetchone()
            if row:
                return Machine(id=row[0], name=row[1])
            return None
        
    @staticmethod
    def get_machine_by_name(machine_name: str) -> Machine:
        """Fetches a machine by its exact name. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM machines WHERE name = ?", (machine_name,))
            row = cursor.fetchone()
            if row:
                return Machine(id=row[0], name=row[1])
            return None
    
    @staticmethod
    def search_machines_by_name(partial_name: str) -> List[Machine]:
        """Searches for machines containing the partial name. Case-insensitive."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name 
                FROM machines 
                WHERE LOWER(name) LIKE LOWER(?) 
                ORDER BY name
            """, (f"%{partial_name}%",))
            rows = cursor.fetchall()
            return [Machine(id=row[0], name=row[1]) for row in rows]
        
    @staticmethod
    def update_machine(machine: Machine):
        """Updates an existing machine in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            # Check if another machine already has this name
            cursor.execute("SELECT id FROM machines WHERE name = ? AND id != ?", (machine.name, machine.id))
            if cursor.fetchone():
                raise ValueError(f"A machine with the name '{machine.name}' already exists.")
            
            cursor.execute("""
                UPDATE machines 
                SET name = ? 
                WHERE id = ?
            """, (machine.name, machine.id))
            conn.commit()

    @staticmethod
    def delete_machine(machine: Machine):
        """Deletes a machine from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM machines WHERE id = ?", (machine.id,))
            conn.commit()
    
    @staticmethod
    def get_all_machines() -> List[Machine]:
        """Returns all machines from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM machines ORDER BY id")
            rows = cursor.fetchall()
            return [Machine(id=row[0], name=row[1]) for row in rows]
    
    @staticmethod
    def print_all_machines():
        """Prints all machines in a formatted way. Just for demo purposes."""
        machines = MachineRepository.get_all_machines()
        if not machines:
            print("No machines found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"{'MACHINES LIST':^60}")
        print(f"{'='*60}")
        for machine in machines:
            print(machine)
        print(f"{'='*60}")
        print(f"Total machines: {len(machines)}")
        print()


class MachineRecipeRepository:
    @staticmethod
    def init_table():
        """Creates the machine_recipes table if it doesn't exist."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS machine_recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    production_capacity REAL NOT NULL,
                    FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    UNIQUE(machine_id, product_id)
                );
            """)
            conn.commit()
    
    @staticmethod
    def add_machine_recipe(recipe: MachineRecipe):
        """Adds a new machine recipe to the database. Returns the recipe with its new ID."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO machine_recipes (machine_id, product_id, production_capacity) 
                VALUES (?, ?, ?)
            """, (recipe.machine_id, recipe.product_id, recipe.production_capacity))
            conn.commit()
            recipe.id = cursor.lastrowid
        return recipe

    @staticmethod
    def get_machine_recipe_by_id(recipe_id: int) -> MachineRecipe:
        """Fetches a machine recipe by its ID. Returns None if not found."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, machine_id, product_id, production_capacity FROM machine_recipes WHERE id = ?", (recipe_id,))
            row = cursor.fetchone()
            if row:
                return MachineRecipe(id=row[0], machine_id=row[1], product_id=row[2], production_capacity=row[3])
            return None
        
    @staticmethod
    def get_recipes_by_machine_id(machine_id: int) -> List[MachineRecipe]:
        """Fetches all recipes for a specific machine."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, machine_id, product_id, production_capacity FROM machine_recipes WHERE machine_id = ?", (machine_id,))
            rows = cursor.fetchall()
            return [MachineRecipe(id=row[0], machine_id=row[1], product_id=row[2], production_capacity=row[3]) for row in rows]
    
    @staticmethod
    def get_recipes_by_product_id(product_id: int) -> List[MachineRecipe]:
        """Fetches all recipes (machines) that can produce a specific product."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, machine_id, product_id, production_capacity FROM machine_recipes WHERE product_id = ?", (product_id,))
            rows = cursor.fetchall()
            return [MachineRecipe(id=row[0], machine_id=row[1], product_id=row[2], production_capacity=row[3]) for row in rows]
        
    @staticmethod
    def update_machine_recipe(recipe: MachineRecipe):
        """Updates an existing machine recipe in the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE machine_recipes 
                SET machine_id = ?, product_id = ?, production_capacity = ? 
                WHERE id = ?
            """, (recipe.machine_id, recipe.product_id, recipe.production_capacity, recipe.id))
            conn.commit()

    @staticmethod
    def delete_machine_recipe(recipe: MachineRecipe):
        """Deletes a machine recipe from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM machine_recipes WHERE id = ?", (recipe.id,))
            conn.commit()
    
    @staticmethod
    def get_all_machine_recipes() -> List[MachineRecipe]:
        """Returns all machine recipes from the database."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, machine_id, product_id, production_capacity FROM machine_recipes ORDER BY id")
            rows = cursor.fetchall()
            return [MachineRecipe(id=row[0], machine_id=row[1], product_id=row[2], production_capacity=row[3]) for row in rows]
    
    @staticmethod
    def print_all_machine_recipes():
        """Prints all machine recipes in a formatted way. Just for demo purposes."""
        recipes = MachineRecipeRepository.get_all_machine_recipes()
        if not recipes:
            print("No machine recipes found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"{'MACHINE RECIPES LIST':^60}")
        print(f"{'='*60}")
        for recipe in recipes:
            print(recipe)
        print(f"{'='*60}")
        print(f"Total machine recipes: {len(recipes)}")
        print()
