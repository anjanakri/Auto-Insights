import google.generativeai as genai
from typing import List, Any, Optional
from dataclasses import dataclass

# Note: We redefine this here to keep the file self-contained for now.
# In a perfect world, this would be in a shared 'types.py' file.
@dataclass
class AgentResponse:
    success: bool
    data: Any
    error: Optional[str] = None
    logs: List[str] = None
    agent_name: str = ""

class AgentArchitect:
    def __init__(self, model: genai.GenerativeModel, memory):
        self.model = model
        self.memory = memory
        self.agent_name = "AgentArchitect"

    def generate_sql(self, user_query: str, error_context: str = "") -> AgentResponse:
        """
        Generates SQL. 
        If 'error_context' is provided, it attempts to FIX the previous SQL.
        """
        logs = [f"[{self.agent_name}] 🤖 Analyzing query..."]
        
        # 1. Get Schema
        schema_context = self.memory.get_schema_context()
        
        # 2. Add Few-Shot Examples (CRITICAL FOR ACCURACY)
        few_shot_examples = """
        Examples:
        Q: "Total sales for Electronics"
        SQL: SELECT sum(amount) FROM sales WHERE product_category = 'Electronics'

        Q: "Top 3 customers by region"
        SQL: SELECT region, count(*) as count FROM customers GROUP BY region ORDER BY count DESC LIMIT 3
        """

        # 3. Base Prompt
        base_prompt = f"""
        You are an expert SQLite analyst.
        
        {schema_context}
        
        {few_shot_examples}
        
        User Query: "{user_query}"
        
        Rules: 
        - Return ONLY the raw SQL query. 
        - No markdown (no ```sql).
        - Use valid SQLite syntax.
        """

        # 4. Dynamic Prompting (The Self-Correction Loop)
        if error_context:
            logs.append(f"[{self.agent_name}] 🔄 Received error feedback. Attempting to fix SQL.")
            prompt = f"""
            {base_prompt}
            
            ⚠️ PREVIOUS ATTEMPT FAILED.
            Error Context:
            {error_context}
            
            TASK: Fix the SQL query above based on the error.
            Fixed SQL:
            """
        else:
            prompt = f"{base_prompt}\nSQL Query:"

        try:
            response = self.model.generate_content(prompt)
            # Clean up response in case Gemini adds markdown
            sql_query = response.text.strip().replace("```sql", "").replace("```", "").strip()
            
            logs.append(f"[{self.agent_name}] ✅ SQL Generated")
            return AgentResponse(success=True, data={'sql': sql_query}, logs=logs, agent_name=self.agent_name)

        except Exception as e:
            return AgentResponse(success=False, data=None, error=str(e), logs=logs, agent_name=self.agent_name)