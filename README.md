
# AutoInsights: The Automated Data Analyst Agent

**AutoInsights** is an Enterprise Multi-Agent System that converts natural language into SQL, executes it against a secure database, and generates visualization + business insights automatically.

> **Built for the Google AI Agents Capstone Competition (Enterprise Track)**

![Status](https://img.shields.io/badge/Status-Functional-success)
![Model](https://img.shields.io/badge/AI-Gemini_2.5_Flash-blue)
![Docker](https://img.shields.io/badge/Deployment-Docker_Ready-blue)

## 🧠 Key Features (Scoring Criteria)
**Multi-Agent System:** 4 Specialized Agents (Architect, Validator, Coder, Storyteller).

**Self-Correction Loop:** If SQL generation fails validation or execution, the error is fed back to the Architect to fix itself.

**Tools:** Custom SQL Executor and Matplotlib Visualization tools.

**Safety:** AgentValidator prevents dangerous operations (DROP/DELETE).

**Deployment:** Docker-ready for immediate cloud scaling.

## 🏗️ Architecture

AutoInsights uses a **Sequential Multi-Agent Architecture** with a **Self-Correction Loop**.

```mermaid
graph LR
    User[User Query] --> Architect[👷 Architect Agent]
    Architect -->|Generate SQL| Validator[🛡️ Validator Agent]
    Validator -->|Pass| Coder[💻 Coder Agent]
    Validator -->|"Fail (Loop)"| Architect
    Coder -->|Execute & Chart| Storyteller[📝 Storyteller Agent]
    Coder -->|"SQL Error (Loop)"| Architect
    Storyteller --> Final[📊 Final Report]

