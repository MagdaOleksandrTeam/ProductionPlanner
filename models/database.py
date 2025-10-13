import sqlite3
from pathlib import Path

DB_PATH = Path("data/production.db")

def get_connection():
    # Create the data directory if it doesn't exist
    DB_PATH.parent.mkdir(exist_ok=True) 
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Creates tables if they don't exist yet."""
    
    if DB_PATH.exists():
        print("Database already exists. Skipping initialization.")
        return
    
    print("Database not found. Initializing...")
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            unit TEXT NOT NULL,
            quantity REAL DEFAULT 0
        );
        """)
        print("Table 'materials' created.")
        conn.commit()
    print("Database initialized successfully!!!")