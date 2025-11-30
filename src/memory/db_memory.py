import sqlite3
from typing import Dict, List, Any
from datetime import datetime

class DatabaseMemory:
    """Memory system for storing schema and query history"""
    
    def __init__(self, db_path: str = "company_data.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.schema = self._load_schema()
        self.query_history = []
        self.session_memory = {}
        
    def _load_schema(self) -> Dict[str, List[str]]:
        """Load database schema"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            schema[table_name] = columns
        
        return schema
    
    def get_schema_context(self) -> str:
        """Format schema for agent context"""
        context = "Database Schema:\n\n"
        for table, columns in self.schema.items():
            context += f"Table: {table}\n"
            context += f"Columns: {', '.join(columns)}\n\n"
        return context
    
    def add_query_history(self, query: str, result: str):
        """Store successful query patterns"""
        self.query_history.append({
            'query': query,
            'result': result,
            'timestamp': datetime.now()
        })
    
    def store_session_data(self, key: str, value: Any):
        """Store session-specific data"""
        self.session_memory[key] = value
    
    def get_session_data(self, key: str) -> Any:
        """Retrieve session-specific data"""
        return self.session_memory.get(key)