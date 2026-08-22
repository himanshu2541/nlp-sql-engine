# ⚡ NLP-SQL Federated Engine



[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(100%25)-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade **Natural Language to Federated SQL Query Engine** that translates plain English queries into validated SQL, routes queries across distributed multi-database environments (**CRM**, **Inventory**, **Sales**), executes cross-database joins in memory, and provides an interactive web dashboard.

---

## 🌟 Key Capabilities

- 🔀 **Federated Multi-Database Engine**: Single-table queries run directly against targeted databases; cross-database queries (`crm.customers` ⟷ `sales.orders`) execute seamlessly via in-memory federation.
- 🔍 **Automated Schema Discovery**: Introspects connected physical databases and infers cross-database relational joins (`orders.customer_id` ⟷ `customers.id`) with zero manual configuration.
- 🛡️ **Two-Tier Security Guardrails**:
  - **Intent Guardrail**: Intercepts greetings and chit-chat with helpful guidance, saving LLM tokens and preventing database hallucinations.
  - **AST Security Guardrail**: Uses `sqlglot` to enforce strictly read-only (`SELECT`) execution, blocking destructive operations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`) and SQL injections.
- 🔄 **Self-Correction Feedback Loop**: Automatically debugs and refines SQL queries if database execution throws an error.
- 🌐 **Modern Interactive Web Dashboard**: Full-stack FastAPI interface with live query execution, syntax-highlighted SQL, interactive results grid, and 1-click CSV/JSON export.
- 🔌 **Pluggable Architecture**:
  - **LLM**: OpenRouter, OpenAI, Local (LM Studio / Ollama), Mock.
  - **Embeddings**: Google Gemini (`text-embedding-004` / `gemini-embedding-001`), OpenAI, HuggingFace, Mock.
  - **Vector Stores**: Local NumPy, Qdrant Cloud, Pinecone.

---

## 🏗️ System Architecture

```
User Prompt (Natural Language)
          │
          ▼
 ┌──────────────────────────────────────────────┐
 │ 0. Intent & Conversational Guardrail        │ ──► (Greeting / Help Message)
 └──────────────────────┬───────────────────────┘
                        │ (Valid Data Query)
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 1. Schema Router (Semantic Vector RAG)       │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 2. Query Planner (Architect LLM)             │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 3. SQL Generator (SQL Developer LLM)         │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 4. AST SQL Security Guardrail (sqlglot)      │ ──► (Blocks Write / Injection)
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 5. Federated Execution (Single DB / Cross-DB)│ ◄──┐ (Self-Correction Loop)
 └──────────────────────┬───────────────────────┘    │
                        │ (On Execution Error) ──────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │ 6. Results Formatter (Web UI / REST API / CLI│
 └──────────────────────────────────────────────┘
```

For in-depth architectural details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Install
```bash
git clone https://github.com/himanshu2541/nlp-sql-engine.git
cd nlp-sql-engine
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```ini
# LLM Provider via OpenRouter
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
LLM_BASE_URL=https://openrouter.ai/api/v1
PLANNER_LLM_PROVIDER=openrouter
PLANNER_LLM_MODEL_NAME=meta-llama/llama-3.3-70b-instruct:free

GENERATION_LLM_PROVIDER=openrouter
GENERATION_LLM_MODEL_NAME=meta-llama/llama-3.3-70b-instruct:free

DEBUG_LLM_PROVIDER=openrouter
DEBUG_LLM_MODEL_NAME=meta-llama/llama-3.3-70b-instruct:free

# Free Google Gemini Embeddings
GEMINI_API_KEY=AIzaSy-your-google-ai-studio-key
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL_NAME=gemini-embedding-001
VECTOR_STORE_PROVIDER=local

# Database Configuration
DB_TYPE=federated
DB_MANAGER=default
```

### 3. Initialize Databases
```bash
python scripts/setup_db.py
```

### 4. Run the Application

- **Interactive Web Dashboard**:
  ```bash
  python -m nlp_sql_engine.web.app
  ```
  Open `http://localhost:8000` in your browser.

- **Command Line Interface (CLI)**:
  ```bash
  python -m nlp_sql_engine.app.main
  ```

---

## 🐳 Docker Deployment

Run the complete stack with zero manual dependencies:

```bash
# 1. First-time build and start
docker compose up --build

# 2. Daily instant start (< 1 second)
docker compose up

# 3. Stop container
docker compose down
```

Access the dashboard at `http://localhost:8000` and Swagger API docs at `http://localhost:8000/docs`.

---

## 🧪 Automated Testing

Run the test suite:
```bash
pytest
```

---

## 📖 Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [Deployment & CI/CD Guide](docs/DEPLOYMENT.md)
- [Sample Questions Reference](questions.txt)

---

## 📄 License
This project is licensed under the MIT License.