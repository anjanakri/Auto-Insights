from autoinsights_adk_python import AutoInsightsOrchestrator, setup_demo_database

def run_evaluation():
    setup_demo_database()
    app = AutoInsightsOrchestrator()
    
    test_cases = [
        {"query": "Show total sales", "expected_keyword": "sales"},
        {"query": "List all products", "expected_keyword": "products"},
        # Add a hard query to test the Loop!
        {"query": "Sales for 'NonExistentCategory'", "expected_keyword": "empty"} 
    ]

    score = 0
    print("🧪 STARTING EVALUATION SUITE")
    print("-" * 30)

    for case in test_cases:
        print(f"Testing: '{case['query']}'")
        result = app.analyze(case['query'])
        
        if result['success']:
            print("  ✅ Success")
            score += 1
        else:
            print(f"  ❌ Failed: {result.get('error')}")

    print("-" * 30)
    print(f"🏁 Final Agent Score: {score}/{len(test_cases)}")

if __name__ == "__main__":
    run_evaluation()