"""
AutoInsights: The Automated Data Analyst Agent
Entry point for the Multi-Agent System.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# === IMPORTS FROM YOUR NEW FOLDERS ===
from src.memory.db_memory import DatabaseMemory
from src.tools.sql_tool import SQLExecutorTool
from src.tools.viz_tool import VisualizationTool
from src.agents.architect import AgentArchitect
from src.agents.others import AgentCoder, AgentStoryteller, AgentValidator, setup_demo_database

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

class AutoInsightsOrchestrator:
    def __init__(self):
        print("🔧 Initializing AutoInsights Agents...")
        
        # 1. Setup Memory & Tools
        self.memory = DatabaseMemory("company_data.db")
        self.sql_tool = SQLExecutorTool(self.memory.connection)
        self.viz_tool = VisualizationTool()
        
        # 2. Setup Models
        #using 'gemini-2.5-flash'
        model_sql = genai.GenerativeModel('gemini-2.5-flash') 
        model_insight = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. Initialize Agents
        self.architect = AgentArchitect(model_sql, self.memory)
        self.validator = AgentValidator()
        self.coder = AgentCoder(self.sql_tool, self.viz_tool)
        self.storyteller = AgentStoryteller(model_insight)
        
        self.all_logs = []

    def analyze(self, user_query: str):
        """
        Main Workflow: Architect -> Validator -> Coder -> Storyteller
        Includes Self-Correction Loop for SQL errors.
        """
        self.all_logs = []
        max_retries = 3
        current_retry = 0
        error_context = ""
        sql = ""
        final_data = None

        print(f"\n🚀 Starting Analysis: {user_query}")
        print("-" * 50)

        # === THE AGENT LOOP (SELF-CORRECTION) ===
        while current_retry < max_retries:
            
            # Step 1: Architect (Generate SQL)
            architect_res = self.architect.generate_sql(user_query, error_context)
            self.all_logs.extend(architect_res.logs)
            print(f"   🤖 Architect: Generated SQL (Attempt {current_retry+1})")
            
            if not architect_res.success:
                return self._fail(architect_res)
            
            sql = architect_res.data['sql']

            # Step 2: Validator (Check Safety)
            validator_res = self.validator.validate_query(user_query, sql)
            self.all_logs.extend(validator_res.logs)
            
            if not validator_res.success:
                print("   ⚠️ Validator: Issues found. Looping back...")
                error_context = f"SQL: {sql}\nValidation Issues: {validator_res.data['issues']}"
                current_retry += 1
                continue # JUMP BACK TO START OF LOOP

            # Step 3: Coder (Execute SQL)
            coder_res = self.coder.execute_and_visualize(sql)
            self.all_logs.extend(coder_res.logs)

            if not coder_res.success:
                print("   ⚠️ Coder: Execution failed. Looping back...")
                error_context = f"SQL: {sql}\nDatabase Error: {coder_res.error}"
                current_retry += 1
                continue # JUMP BACK TO START OF LOOP
            
            # Success!
            final_data = coder_res.data
            print("   ✅ Coder: Execution Successful!")
            break
        
        # Check if we failed after max retries
        if current_retry >= max_retries:
            return {"success": False, "error": "Max retries exceeded. Could not generate valid SQL."}

        # Step 4: Storyteller (Generate Insights)
        print("   📊 Storyteller: Generating business insights...")
        story_res = self.storyteller.generate_insights(
            user_query, 
            final_data['dataframe'], 
            final_data['chart_type']
        )
        self.all_logs.extend(story_res.logs)

        return {
            "success": True,
            "sql": sql,
            "chart": final_data['chart'],
            "insights": story_res.data['insights'],
            "logs": self.all_logs
        }

    def _fail(self, res):
        return {"success": False, "error": res.error, "logs": self.all_logs}

# === RUN THE APP ===
if __name__ == "__main__":
    # 1. Create the dummy database first
    setup_demo_database()
    
    # 2. Start the Agent
    app = AutoInsightsOrchestrator()
    
    # 3. Ask a question
    question = "Why did sales drop in Q3 for electronics?"
    result = app.analyze(question)
    
    # 4. Show results
    if result['success']:
        print("\n" + "="*50)
        print("📝 FINAL REPORT")
        print("="*50)
        print(f"SQL Used: {result['sql']}")
        print("\n--- INSIGHTS ---")
        print(result['insights'])
        print("\n✅ Analysis Complete. Chart generated (Base64).")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        # Print logs to see what happened
        for log in result.get('logs', []):
            print(log)