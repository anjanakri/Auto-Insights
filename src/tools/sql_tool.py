import sqlite3
import pandas as pd

class SQLExecutorTool:
    """Tool for executing SQL queries safely"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.whitelist_tables = ['sales', 'products', 'customers']
        
    def execute(self, sql: str) -> pd.DataFrame:
        """Execute SQL with safety checks"""
        sql_lower = sql.lower()
        
        # Check for dangerous operations
        if any(keyword in sql_lower for keyword in ['drop', 'delete', 'update', 'insert', 'alter']):
            raise ValueError("Only SELECT queries are allowed")
        
        try:
            df = pd.read_sql_query(sql, self.connection)
            return df
        except Exception as e:
            raise Exception(f"SQL execution failed: {str(e)}")