# 🤖 DSA Solver Project - Multi-Agent Intelligent System

A comprehensive **multi-agent intelligent system** for solving Data Structures and Algorithms (DSA) problems using **CrewAI**, **Google ADK (Application Development Kit, and **Google Gemini AI**.

The system combines specialized AI agents that work together to analyze DSA problems, generate test cases, write optimized code solutions, and validate implementations—all with intelligent reasoning and complexity analysis.

---

## 🎯 Project Overview

**DSA Solver** is an advanced learning platform designed to help developers:

- 📝 Understand complex DSA problems through intelligent analysis
- 🧪 Generate comprehensive test cases automatically
- 💻 Generate optimized code solutions in multiple languages
- ✅ Validate solutions with automated testing
- 📊 Analyze algorithmic complexity (Time & Space)
- 🔗 Extract problems from LeetCode, Codeforces, GeeksforGeeks, and more

### Use Cases

- **Learning DSA**: Get AI-assisted analysis and explanations of problems
- **Interview Preparation**: Practice with auto-generated test cases and solutions
- **Code Validation**: Automatically verify if your solution works
- **Algorithm Analysis**: Understand time and space complexity

---

## ✨ Key Features

✅ **Multi-Agent System**: Specialized agents for different tasks (Reasoning, Code Generation, Testing, Validation, Complexity Analysis)  
✅ **Context Sharing**: Intermediate outputs flow between agents via STM (Short-Term Memory)  
✅ **MCP Tools**: Model Context Protocol integration (Code Executor, Complexity Analyzer, Web Search)  
✅ **Structured Output**: Pydantic models for type-safe data structures  
✅ **Monitoring & Logging**: Comprehensive callback system with detailed execution tracking  
✅ **A2A Protocol**: Agent-to-Agent communication using HTTP/JSON (CrewAI ↔ ADK)  
✅ **Multi-Language Support**: Python, C++, Java code generation and execution  
✅ **Web Integration**: Extract problem statements from major coding platforms  
✅ **AI-Powered**: Google Gemini API for intelligent reasoning and code generation

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    🖥️ Streamlit Frontend                       │
│         (User Input: Problem Text, Link, Language)            │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  🔄 Coordinator Agent (CrewAI)      │
        │     - Orchestrates workflow         │
        │     - Manages task execution        │
        │     - Tracks session context        │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────┴────────────────────────────┐
        │                                              │
        ▼                                              ▼
   ┌──────────────────┐                      ┌─────────────────────┐
   │ 🧠 Reasoner      │ Parallel            │ 🧪 Test Generator   │
   │ Agent           │ Execution           │ Agent               │
   │                 │                      │                     │
   │ • Analyzes DSA  │                      │ • Creates test      │
   │   patterns      │                      │   cases             │
   │ • Identifies    │                      │ • Handles edge      │
   │   approach      │                      │   cases             │
   │ • Finds similar │                      │ • Generates         │
   │   problems      │                      │   input/output      │
   └──────────────────┘                      └─────────────────────┘
        │                                              │
        └──────────────────┬───────────────────────────┘
                          │ (Results stored in STM)
                          ▼
        ┌─────────────────────────────────────┐
        │  💻 Code Generator Agent            │
        │     • Generates optimal code        │
        │     • Supports multiple languages   │
        │     • Considers DSA analysis        │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  ✅ Validator Agent                 │
        │     • Runs test cases               │
        │     • Captures output               │
        │     • Validates correctness         │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  📊 Complexity Analyzer             │
        │     • Analyzes Time Complexity      │
        │     • Analyzes Space Complexity     │
        │     • Provides optimization hints   │
        └──────────────────────────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │                                    │
        ▼ (HTTP A2A Protocol)              (STM Memory)
   ┌──────────────────────────┐             │
   │ 🎯 ADK Specialist Agent  │◄────────────┘
   │ (FastAPI Server)         │
   │                          │
   │ • Coordinates with       │
   │   MCP tools              │
   │ • Executes code          │
   │ • Analyzes complexity    │
   │ • Web search            │
   └──────────────────────────┘
              │
    ┌─────────┼──────────┐
    │         │          │
    ▼         ▼          ▼
  ┌───┐   ┌────────┐   ┌─────────┐
  │🔧│   │🔍Search│   │📈Complex│
  │Exec│  │ Web    │   │ Analyzer│
  └───┘   └────────┘   └─────────┘
  (MCP Tools - External Integration)
```

---

## 📁 Project Structure

```
dsa_solver_project/
├── app.py                          # 🖥️ Streamlit Frontend
│
├── adk_agent/                      # 🎯 ADK Specialist Agent (FastAPI)
│   ├── main.py                     # FastAPI app initialization
│   ├── routes.py                   # API endpoints (/dsa)
│   ├── specialist_agent.py         # Main request handler
│   ├── pydantic_models.py          # Data models (DSAResult, TestCase, etc)
│   └── mcp/                        # Model Context Protocol Tools
│       ├── code_executor.py        # Execute Python/C++/Java code
│       ├── complexity_analyzer.py  # Analyze algorithmic complexity
│       └── web_search.py           # Search for similar problems
│
├── agent/                          # 🧠 Intelligent Agents
│   ├── reasoner_agent.py           # Problem analysis & DSA reasoning
│   ├── test_generator_agent.py     # Generate test cases
│   ├── code_generator_agent.py     # Generate solution code
│   ├── validator_agent.py          # Validate solutions
│   └── complexity_agent.py         # Complexity analysis
│
├── crew/                           # 🔄 CrewAI Orchestration
│   ├── crewai_agents.py            # Define CrewAI agents
│   ├── coordinator_agent_v2.py     # Main coordination logic
│   ├── callbacks.py                # Execution callbacks & logging
│   ├── agent_tools.py              # LangChain tools for agents
│   ├── langchain_tools.py          # Additional LangChain utilities
│   ├── a2a_client_tool.py          # HTTP client for A2A protocol
│   └── run_coordinator.py          # Entry point for CrewAI execution
│
├── shared/                         # 📦 Shared Utilities
│   ├── config.py                   # Configuration & environment variables
│   └── memory.py                   # STM (Short-Term Memory) implementation
│
├── utils/                          # 🛠️ Utility Functions
│   └── gemini_wrapper.py           # Google Gemini API wrapper
│
├── test/                           # 🧪 Sample Data
│   └── sample_problem.json         # Sample DSA problem for testing
│
├── output/                         # 📤 Output Artifacts
│   └── Streamlit_Submitted_Problem_result.md  # Results output
│
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## 🛠️ Technology Stack

| Component               | Technology                | Purpose                         |
| ----------------------- | ------------------------- | ------------------------------- |
| **UI/Frontend**         | Streamlit                 | Web interface for problem input |
| **Agent Orchestration** | CrewAI                    | Multi-agent workflow management |
| **Google Integration**  | Google ADK, Gemini API    | AI reasoning & code generation  |
| **Backend Framework**   | FastAPI, Uvicorn          | REST API for specialist agent   |
| **Agent Framework**     | LangChain, LangGraph      | AI reasoning chains and graphs  |
| **AI Model**            | Google Gemini             | Language model for intelligence |
| **Data Models**         | Pydantic                  | Type-safe data structures       |
| **Memory**              | STM (In-Memory)           | Context sharing between agents  |
| **Code Execution**      | Python subprocess         | Execute generated code safely   |
| **Logging**             | Python logging, JSON logs | Track execution flow            |

---

## 📋 Agent Descriptions

### 1. **🧠 Reasoner Agent** (`agent/reasoner_agent.py`)

- Analyzes DSA problems to identify:
  - Core algorithm patterns (sorting, searching, DP, graphs, etc.)
  - Recommended approach/algorithm
  - Edge cases and corner scenarios
  - Related problems and patterns
- Uses Google Gemini for intelligent analysis
- Stores results in STM for other agents to use

### 2. **🧪 Test Generator Agent** (`agent/test_generator_agent.py`)

- Generates comprehensive test cases:
  - Basic test cases
  - Edge cases (empty input, boundary values, single elements, etc.)
  - Large input scenarios
  - Error cases
- Each test case includes input and expected output
- JSON formatted for validator consumption

### 3. **💻 Code Generator Agent** (`agent/code_generator_agent.py`)

- Generates optimized solution code
- Supports multiple languages:
  - Python
  - C++
  - Java
- Uses problem analysis from Reasoner Agent
- Produces clean, documented code with comments

### 4. **✅ Validator Agent** (`agent/validator_agent.py`)

- Executes generated code against test cases
- Reports:
  - Test case pass/fail status
  - Actual output vs expected output
  - Runtime errors and exceptions
- Uses Code Executor MCP tool
- Provides detailed validation results

### 5. **📊 Complexity Agent** (`agent/complexity_agent.py`)

- Analyzes algorithmic complexity:
  - Time Complexity (Big-O notation)
  - Space Complexity
  - Optimization opportunities
- Provides explanations for complexity calculations
- Compares with alternative approaches

### 6. **🔄 Coordinator Agent** (`crew/coordinator_agent_v2.py`)

- Orchestrates the entire workflow:
  - Calls Reasoner and Test Generator in parallel
  - Passes context to Code Generator
  - Manages validation and complexity analysis
  - Handles errors gracefully
- Uses CrewAI for robust task management

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- Streamlit
- FastAPI
- CrewAI and dependencies (see `requirements.txt`)

### Installation

1. **Clone/Extract the project**

   ```bash
   cd dsa_solver_project
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ADK_A2A_URL=http://localhost:8000/dsa
   SERPAPI_KEY=your_serpapi_key_here  # Optional for web search
   LTM_DB_PATH=./shared/ltm.db
   REDIS_URL=  # Optional for Redis caching
   ```

---

## 📱 Usage

### Running the System

1. **Start the ADK Specialist Agent (FastAPI Server)**

   ```bash
   python -m uvicorn adk_agent.main:app --host 0.0.0.0 --port 8000
   ```

2. **In a new terminal, start the Streamlit Frontend**

   ```bash
   streamlit run app.py
   ```

3. **Open the Streamlit UI**
   - Navigate to `http://localhost:8501` in your browser
   - Enter a DSA problem description or paste a link
   - Select the programming language
   - Click "Solve Problem"

### Supported Input Sources

- **Direct Text**: Paste the problem description directly
- **LeetCode**: Paste a LeetCode problem link
- **Codeforces**: Paste a Codeforces problem link
- **GeeksforGeeks (GFG)**: Paste a GFG problem link

### Example Input

```
Merge two sorted arrays into a single sorted array without using extra space.

Input: arr1 = [1, 5, 9], arr2 = [2, 3, 8]
Output: [1, 2, 3, 5, 8, 9]

Constraints:
- Cannot use extra space
- Must be O(n+m) time complexity
```

---

## 🔄 Workflow

1. **Input Processing**
   - User enters problem via Streamlit UI
   - System extracts problem text (if link provided)
   - Selects target programming language

2. **Parallel Analysis** (Pre-computation)
   - **Reasoner Agent**: Analyzes problem to identify DSA patterns
   - **Test Generator**: Creates comprehensive test cases
   - Both run in parallel for speed

3. **Solution Generation**
   - **Code Generator**: Uses analysis to generate optimal code
   - Incorporates insights from Reasoner Agent

4. **Validation**
   - **Validator Agent**: Runs generated code against test cases
   - Executes code safely using subprocess
   - Reports pass/fail for each test case

5. **Complexity Analysis**
   - **Complexity Agent**: Analyzes time/space complexity
   - Provides optimization suggestions

6. **Result Output**
   - Comprehensive results shown in Streamlit UI
   - Results saved to output files

---

## 🔌 MCP Tools (Model Context Protocol)

### 1. **Code Executor** (`adk_agent/mcp/code_executor.py`)

- **Purpose**: Safely execute Python/C++/Java code
- **Supports**:
  - LeetCode-style classes
  - Codeforces-style stdin/stdout
  - Multiple programming languages
- **Features**:
  - Timeout protection (default 5s)
  - Output capture (stdout/stderr)
  - Error handling

### 2. **Complexity Analyzer** (`adk_agent/mcp/complexity_analyzer.py`)

- **Purpose**: Analyze algorithmic complexity
- **Analyzes**: Time and Space complexity
- **Returns**: Big-O notation with explanations

### 3. **Web Search** (`adk_agent/mcp/web_search.py`)

- **Purpose**: Find similar/related DSA problems
- **Integrates**: SerpAPI for web search
- **Helps**: Identify similar patterns and solutions

---

## 📊 Output Format

### Streamlit UI Output

The system displays comprehensive results including:

- ✅ **Problem Analysis**: Topic, pattern, approach, edge cases
- ✅ **Generated Test Cases**: Input/output pairs
- ✅ **Generated Solution Code**: Syntax-highlighted code
- ✅ **Validation Results**: Pass/fail status for each test
- ✅ **Complexity Analysis**: Time and space complexity
- ✅ **Execution Logs**: Detailed event tracking

### JSON Output Format

```json
{
  "session_id": "uuid-string",
  "problem": "problem text",
  "language": "python",
  "analysis": {
    "topic": "Array/Sorting",
    "pattern": "Two Pointer",
    "approach": "...",
    "edge_cases": [...]
  },
  "generated_code": "def merge_sorted_arrays(...)",
  "test_results": [
    {
      "input": "[1,5,9],[2,3,8]",
      "expected": "[1,2,3,5,8,9]",
      "actual": "[1,2,3,5,8,9]",
      "passed": true
    }
  ],
  "complexity": {
    "time": "O(n+m)",
    "space": "O(1)"
  }
}
```

---

## 🔗 Communication Protocols

### A2A Protocol (Agent-to-Agent)

- **Method**: HTTP POST
- **Format**: JSON
- **Flow**: CrewAI → ADK Specialist Agent → MCP Tools
- **Purpose**: Seamless communication between different agent systems

### STM (Short-Term Memory)

- **Type**: In-memory session storage
- **Purpose**: Share intermediate results between agents
- **Lifetime**: Single session duration
- **Data**: Problem analysis, test cases, code, validation results

---

## 📝 Configuration

### Environment Variables (`.env`)

```env
# Required
GEMINI_API_KEY=your_api_key

# Optional
ADK_A2A_URL=http://localhost:8000/dsa
SERPAPI_KEY=your_key
LTM_DB_PATH=./shared/ltm.db
REDIS_URL=redis://localhost:6379
```

### Configuration File (`shared/config.py`)

- Loads environment variables
- Provides default paths and URLs
- API key management

---

## 🐛 Troubleshooting

| Issue                           | Solution                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------- |
| `GEMINI_API_KEY not set`        | Add `GEMINI_API_KEY` to `.env` file                                             |
| `Connection refused on :8000`   | Ensure ADK Agent is running: `python -m uvicorn adk_agent.main:app --port 8000` |
| `Streamlit port already in use` | Use `streamlit run app.py --server.port 8502`                                   |
| `Code execution timeout`        | Increase timeout in `code_executor.py` or optimize code                         |
| `JSON extraction failed`        | Check Gemini API response format in agent logs                                  |

---

## 📚 Learning Resources

- **CrewAI Docs**: https://docs.crewai.com
- **LangChain Docs**: https://python.langchain.com
- **Google Gemini API**: https://ai.google.dev
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io

---

## 🤝 Contributing

To improve the system:

1. Add new agent specializations in `agent/` directory
2. Extend MCP tools in `adk_agent/mcp/`
3. Add more language support in Code Generator
4. Improve complexity analysis algorithms
5. Enhance test case generation heuristics

---

## 📄 License

This project is for educational purposes within the GenAI/ADK Learning course.

---

## 👥 Project Team

**Course**: GenAI and LLM - Learning ADK  
**Semester**: 7

---

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review execution logs in `dsa_logs.jsonl`
3. Check agent outputs in Streamlit terminal
4. Review FastAPI logs (port 8000)

---

**Last Updated**: April 2026  
**Status**: Active Development
│ Structured │
│ Output (Pydantic)│
└─────────────────┘

````

## Installation

1. **Clone the repository** (if applicable)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
````

3. **Set up environment variables** (create `.env` file):

```env
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_KEY=your_serper_api_key  # Optional, for web search
ADK_A2A_URL=http://localhost:8000/a2a
```

## Running the Project

### Step 1: Start the ADK Agent (FastAPI)

In one terminal:

```bash
uvicorn adk_agent.main:app --reload --port 8000
```

The ADK agent will be available at `http://localhost:8000`

### Step 2: Run the Streamlit Application

In another terminal:

```bash
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

**Note:** CrewAI agents run automatically when you submit a problem in the Streamlit app. The coordinator (`crew/coordinator_agent_v2.py`) creates and executes the CrewAI crew internally - no separate command needed!

**How it works:**

1. User submits problem in Streamlit → triggers `coordinate()` function
2. Coordinator automatically creates CrewAI crew with 5 agents
3. CrewAI agents execute sequentially (TestGenerator → Reasoner → CodeGenerator → Validator → Complexity)
4. Results sent to ADK agent via A2A protocol
5. Final structured output displayed in Streamlit

See `HOW_IT_WORKS.md` for detailed execution flow.

## Usage

1. Open the Streamlit app in your browser
2. Enter a DSA problem description or paste a LeetCode/Codeforces/GFG link
3. Select the programming language (Python, C++, Java)
4. Click "Solve Problem"
5. View the generated solution, test results, complexity analysis, and similar problems

## Project Structure

```
dsa_solver_project/
├── adk_agent/              # ADK agent implementation
│   ├── main.py             # FastAPI app
│   ├── routes.py           # A2A endpoint
│   ├── specialist_agent.py  # ADK specialist agent
│   ├── pydantic_models.py  # Structured output models
│   └── mcp/                # MCP tools
│       ├── code_executor.py
│       ├── complexity_analyzer.py
│       └── web_search.py
├── crew/                   # CrewAI implementation
│   ├── coordinator_agent_v2.py  # Main coordinator
│   ├── crewai_agents.py    # CrewAI agent definitions
│   ├── langchain_tools.py  # LangChain tool wrappers
│   ├── callbacks.py        # Monitoring callbacks
│   └── a2a_client_tool.py  # A2A client
├── agent/                  # Legacy agent classes (can be removed)
├── shared/                 # Shared utilities
│   ├── memory.py           # STM/LTM implementation
│   └── config.py           # Configuration
├── utils/                  # Utility functions
│   └── gemini_wrapper.py   # Gemini API wrapper
├── app.py                  # Streamlit UI
├── requirements.txt         # Dependencies
└── PROJECT_REQUIREMENTS_CHECK.md  # Requirements verification
```

## Key Components

### 1. Context Sharing (STM)

- Implemented in `shared/memory.py`
- Agents share context via `STM_STORE`
- CrewAI tasks use `context` parameter for dependencies
- Your existing agents from `agent/` folder use STM_STORE automatically

### 2. MCP Tools

- **Code Executor**: Executes and validates Python code
- **Complexity Analyzer**: Analyzes time/space complexity
- **Web Search**: Finds similar DSA problems

### 3. Structured Output

- All outputs use Pydantic models (`DSAResult`, `TestCase`, `TestCaseResult`)
- Defined in `adk_agent/pydantic_models.py`

### 4. Monitoring & Logging

- `CrewAICallback` class in `crew/callbacks.py`
- Logs to `dsa_logs.jsonl` (JSON Lines format)
- Tracks agent execution, task flows, and errors

### 5. A2A Protocol

- Request: `{"type": "request", "action": "dsa_solve", "payload": {...}}`
- Response: Structured Pydantic model (converted to dict)
- Implemented in `crew/a2a_client_tool.py` and `adk_agent/routes.py`

### 6. Frameworks

- **CrewAI**: Agent orchestration (`crew/crewai_agents.py`)
  - Uses your existing agents from `agent/` folder via `crew/agent_tools.py`
  - Wraps your agents (TestGeneratorAgent, DSAReasonerAgent, etc.) as LangChain tools
- **ADK**: Specialist agent (`adk_agent/specialist_agent.py`)
- **LangChain**: Tool integration (`crew/langchain_tools.py` and `crew/agent_tools.py`)

## Testing

### Test A2A Communication

```bash
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "type": "request",
    "action": "dsa_solve",
    "payload": {
      "title": "Test Problem",
      "problem_text": "Find the median of two sorted arrays",
      "language": "python",
      "sample_tests": []
    }
  }'
```

### Check Logs

Monitor execution in `dsa_logs.jsonl`:

```bash
tail -f dsa_logs.jsonl
```

## Requirements Compliance

All 6 requirements are met:

1. ✅ Context Sharing via STM
2. ✅ MCP Tools (3 tools)
3. ✅ Structured Output (Pydantic)
4. ✅ Monitoring & Logging (Callbacks)
5. ✅ A2A Protocol (CrewAI ↔ ADK)
6. ✅ Frameworks (CrewAI + ADK + LangChain)

See `PROJECT_REQUIREMENTS_CHECK.md` for detailed verification.

## Troubleshooting

1. **ADK agent not responding**: Ensure FastAPI server is running on port 8000
2. **Missing API keys**: Check `.env` file has `GEMINI_API_KEY` set
3. **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
4. **Context not sharing**: Check STM_STORE is being used correctly in coordinator

## Contributors
Harshit Jain
