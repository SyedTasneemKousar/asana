"""
Database connection and schema management.
Handles SQLite database creation and connection.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database connection manager"""
    
    def __init__(self, db_path: str):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        output_dir = Path(self.db_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """Create and return database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        return self.conn
    
    def initialize_schema(self, schema_file: str = 'schema.sql'):
        """
        Initialize database schema from SQL file
        
        Args:
            schema_file: Path to schema SQL file
        """
        schema_path = Path(schema_file)
        if not schema_path.exists():
            # Try relative to project root
            schema_path = Path(__file__).parent.parent.parent / schema_file
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        conn = self.connect()
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema initialized")
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL statement"""
        conn = self.connect()
        return conn.execute(sql, params)
    
    def executemany(self, sql: str, params_list: list) -> sqlite3.Cursor:
        """Execute SQL statement multiple times"""
        conn = self.connect()
        return conn.executemany(sql, params_list)
    
    def commit(self):
        """Commit transaction"""
        if self.conn:
            self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            self.commit()
        self.close()
    
    def get_table_count(self, table_name: str) -> int:
        """Get count of rows in a table"""
        conn = self.connect()
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]

