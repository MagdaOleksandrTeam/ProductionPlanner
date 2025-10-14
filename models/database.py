import sqlite3
from pathlib import Path

DB_PATH = Path("data/production.db")

class ConnectionManager:
    """Manages database connections with proper cleanup."""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Gets or creates a database connection."""
        if self._connection is None:
            DB_PATH.parent.mkdir(exist_ok=True)
            self._connection = sqlite3.connect(DB_PATH)
        return self._connection
    
    def close_connection(self):
        """Closes the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close_connection()

# Global connection manager instance
_connection_manager = ConnectionManager()

def get_connection():
    """Gets a shared database connection."""
    return _connection_manager.get_connection()

def close_db():
    """Closes the shared database connection."""
    _connection_manager.close_connection()

def init_db():
    """Creates the database file and initializes all tables."""
    
    # Create the data directory if it doesn't exist
    DB_PATH.parent.mkdir(exist_ok=True)
    
    if DB_PATH.exists():
        print("Database already exists.")
    else:
        print("Database not found. Creating database file...")
    
    # Initialize all repository tables (this will create the file if it doesn't exist)
    print("Initializing database tables...")
    
    # Import here to avoid circular imports
    from .material import MaterialRepository
    
    # Initialize tables for all repositories - this will create the DB file properly
    MaterialRepository.init_table()
    
    print("Materials table initialized.")
    
    print("Database initialization completed successfully!")