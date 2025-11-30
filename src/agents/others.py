import google.generativeai as genai
from google.generativeai import types
import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import the tools these agents need to use
from src.tools.sql_tool import SQLExecutorTool
from src.tools.viz_tool import VisualizationTool

# Re-defining the response format here so these agents can use it
@dataclass
class AgentResponse:
    success: bool
    data: Any
    error: Optional[str] = None
    logs: List[str] = None
    agent_name: str = ""

# ==========================================
# AGENT B: THE CODER
# ==========================================
class AgentCoder:
    """
    Agent B: The Execution and Visualization Agent
    """
    
    def __init__(self, sql_tool: SQLExecutorTool, viz_tool: VisualizationTool):
        self.sql_tool = sql_tool
        self.viz_tool = viz_tool
        self.agent_name = "AgentCoder"
        
    def execute_and_visualize(self, sql: str, chart_type: str = 'bar') -> AgentResponse:
        """Execute SQL and create visualization"""
        logs = [f"[{self.agent_name}] 💻 Executing SQL query"]
        
        try:
            # Execute SQL
            df = self.sql_tool.execute(sql)
            logs.append(f"[{self.agent_name}] ✅ Query returned {len(df)} rows, {len(df.columns)} columns")
            
            # Auto-detect chart type
            if len(df) > 10:
                chart_type = 'line'
            
            # Generate chart
            chart_base64 = self.viz_tool.create_chart(df, chart_type)
            logs.append(f"[{self.agent_name}] 📊 Generated {chart_type} chart")
            
            return AgentResponse(
                success=True,
                data={
                    'dataframe': df,
                    'chart': chart_base64,
                    'chart_type': chart_type,
                    'row_count': len(df),
                    'column_count': len(df.columns)
                },
                logs=logs,
                agent_name=self.agent_name
            )
            
        except Exception as e:
            logs.append(f"[{self.agent_name}] ❌ Error: {str(e)}")
            return AgentResponse(
                success=False,
                data=None,
                error=str(e),
                logs=logs,
                agent_name=self.agent_name
            )

# ==========================================
# AGENT C: THE STORYTELLER
# ==========================================
class AgentStoryteller:
    """
    Agent C: The Insight Generator Agent
    """
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.agent_name = "AgentStoryteller"
        
    def generate_insights(self, user_query: str, df: pd.DataFrame, 
                          chart_context: str) -> AgentResponse:
        """Generate business insights from data"""
        logs = [f"[{self.agent_name}] 📊 Analyzing data for insights"]
        
        # Prepare data summary
        numeric_cols = df.select_dtypes(include=['number']).columns
        data_summary = f"""
Data Overview:
- Total Records: {len(df)}
- Columns: {', '.join(df.columns)}
- Chart Type: {chart_context}

Sample Data (First 5 rows):
{df.head(5).to_string()}

Statistical Analysis:
{df.describe().to_string() if len(numeric_cols) > 0 else 'No numeric data available'}
"""
        
        prompt = f"""You are a Senior Business Intelligence Analyst.

ORIGINAL BUSINESS QUESTION: "{user_query}"

{data_summary}

Provide a comprehensive executive analysis with:
1. EXECUTIVE SUMMARY
2. KEY FINDINGS (Data-backed)
3. TREND ANALYSIS
4. BUSINESS RECOMMENDATIONS
5. RISK ASSESSMENT

Be specific and professional.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000
                )
            )
            
            insights = response.text
            logs.append(f"[{self.agent_name}] ✅ Generated insights")
            
            return AgentResponse(
                success=True,
                data={'insights': insights},
                logs=logs,
                agent_name=self.agent_name
            )
            
        except Exception as e:
            return AgentResponse(success=False, data=None, error=str(e), logs=logs, agent_name=self.agent_name)

# ==========================================
# AGENT D: THE VALIDATOR
# ==========================================
class AgentValidator:
    """
    Agent D: Safety and Validation Agent
    """
    
    def __init__(self):
        self.agent_name = "AgentValidator"
        
    def validate_query(self, user_query: str, sql: str) -> AgentResponse:
        """Validate for safety and correctness"""
        logs = [f"[{self.agent_name}] 🔒 Running safety validation"]
        issues = []
        
        sql_lower = sql.lower()
        
        # Security checks
        dangerous_operations = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
        for operation in dangerous_operations:
            if operation in sql_lower:
                issues.append(f"🚫 Dangerous operation detected: {operation.upper()}")
        
        if issues:
            logs.append(f"[{self.agent_name}] ❌ Validation FAILED")
            return AgentResponse(
                success=False,
                data={'issues': issues},
                error="SQL validation failed",
                logs=logs,
                agent_name=self.agent_name
            )
        
        logs.append(f"[{self.agent_name}] ✅ Validation PASSED")
        return AgentResponse(success=True, data={'issues': []}, logs=logs, agent_name=self.agent_name)

# ==========================================
# DATABASE SETUP HELPER
# ==========================================
def setup_demo_database():
    """Create demo database with realistic business data"""
    conn = sqlite3.connect("company_data.db")
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product_category TEXT,
            amount REAL,
            sale_date TEXT,
            region TEXT,
            customer_id INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            inventory INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            region TEXT,
            signup_date TEXT
        )
    """)
    
    # Insert realistic sample data
    sample_sales = [
        (1, 'Electronics', 45000, '2024-07-15', 'North', 1),
        (2, 'Electronics', 42000, '2024-07-22', 'North', 2),
        (3, 'Electronics', 38000, '2024-08-10', 'South', 3),
        (4, 'Electronics', 35000, '2024-08-25', 'East', 4),
        (5, 'Electronics', 29000, '2024-09-05', 'West', 5),
        (6, 'Electronics', 27000, '2024-09-20', 'North', 6),
        (7, 'Clothing', 32000, '2024-07-12', 'South', 7),
        (8, 'Clothing', 35000, '2024-08-08', 'East', 8),
        (9, 'Clothing', 31000, '2024-09-15', 'West', 9),
        (10, 'Home & Garden', 28000, '2024-07-20', 'North', 10),
        (11, 'Home & Garden', 30000, '2024-08-18', 'South', 11),
        (12, 'Home & Garden', 33000, '2024-09-10', 'East', 12),
    ]
    
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)", sample_sales)
    conn.commit()
    conn.close()
    print("✅ Demo database created!")