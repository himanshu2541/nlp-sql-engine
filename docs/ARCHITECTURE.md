# System Architecture & Technical Specifications

The **NLP-SQL Federated Engine** converts ambiguous Natural Language questions into precise SQL queries, routes them across multiple disjoint databases (CRM, Inventory, Sales), performs in-memory cross-database joins, and validates query safety.

---

## 1. High-Level Architectural Diagram

```mermaid
flowchart TD
    User([User Request]) --> Guardrail[Intent & Conversational Guardrail]
    Guardrail -- Casual Chat / Greeting --> ConversationalResponse([Help & Guided Prompts])
    Guardrail -- Valid Data Request --> Router[Schema Router & Semantic Index]
    
    subgraph Vector RAG Layer
        Embedder[Gemini / Mock Embedder] --> VectorDB[(Vector Store: Qdrant / Pinecone / Local)]
        Router <--> VectorDB
    end

    Router --> Planner[Step 1: Architect / Planning LLM]
    Planner --> Generator[Step 2: SQL Generator LLM]
    Generator --> SQLGuardrail[Step 3: AST Security & Limit Guardrail]
    
    SQLGuardrail --> FedAdapter{Federated Database Adapter}
    
    subgraph Multi-Database Layer
        FedAdapter -- Single DB --> CRM[(crm.db)]
        FedAdapter -- Single DB --> INV[(inventory.db)]
        FedAdapter -- Single DB --> SALES[(sales.db)]
        FedAdapter -- Cross-DB Join --> MemJoin[In-Memory SQLite Engine]
    end

    FedAdapter -- Error Caught --> Debugger[Step 4: Self-Correction Debugger]
    Debugger --> Generator

    FedAdapter --> UI[Interactive Dashboard / REST API]
```

---

## 2. Core Architectural Pillars

### A. Intent & Conversational Guardrail (`nlp_sql_engine/core/security/intent_guardrail.py`)
- Intercepts non-database queries (`"Hello"`, `"Help"`, `"What can you do?"`, chit-chat) **before** invoking LLMs or executing SQL.
- Prevents database hallucinations and saves API tokens.

### B. Auto Schema Discovery & Relationship Linker (`nlp_sql_engine/services/schema_discovery.py`)
- Introspects connected physical databases dynamically on boot.
- Infers foreign keys and cross-database joins via naming heuristics (`orders.customer_id` ⟷ `customers.id`).
- Removes the need for manual virtual schema definitions.

### C. AST SQL Security Guardrail (`nlp_sql_engine/core/security/guardrail.py`)
- Parses SQL Abstract Syntax Trees (AST) using `sqlglot`.
- Enforces strict read-only execution (`SELECT` only).
- Blocks destructive operations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`).
- Enforces safe query limits to prevent out-of-memory crashes.

### D. Federated Multi-Database Execution (`nlp_sql_engine/infra/database/federated_adapter.py`)
- **Single DB Routing**: If all referenced tables reside in a single database (e.g. `inventory.products`), queries are transpiled and pushed down directly to that database engine.
- **Cross-DB In-Memory Joins**: If queries span multiple disjoint databases (e.g. `sales.orders` joined with `crm.customers`), data slices are pulled concurrently and joined in an isolated in-memory SQLite virtual instance.

### E. Self-Correction Feedback Loop (`nlp_sql_engine/use_cases/ask_question.py`)
- If the database engine returns a syntax or execution error, the `Debugger` step automatically inspects the error message, schema, and failed SQL to refine and regenerate a working query.

---

## 3. Supported Infrastructure Providers

| Component | Registered Providers |
| :--- | :--- |
| **LLM Engine** | `openrouter` (OpenRouter API), `openai` (OpenAI API), `local` (LM Studio / Ollama), `mock` |
| **Embeddings** | `gemini` (Google AI Studio `text-embedding-004` / `gemini-embedding-001`), `openai`, `huggingface`, `mock` |
| **Vector Store** | `local` (NumPy vectorized cosine similarity), `qdrant` (Qdrant Cloud/Local), `pinecone` (Pinecone Cloud) |
| **Database** | `federated` (Multi-DB orchestrator), `sqlalchemy`, `sqlite` |
