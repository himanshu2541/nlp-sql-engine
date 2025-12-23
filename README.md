# NLP SQL Engine

A natural language to SQL query engine that converts user questions into SQL queries and executes them against a database.

## Features

- Multiple LLM providers (OpenAI, Phi-3 Mini, Mock)
- Multiple embedding providers (OpenAI, HuggingFace)
- SQLite database adapter
- Modular architecture with registries and factories

## Installation

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Set up environment variables in `.env` file:
   ```
   API_KEY=your_openai_api_key
   ```

## Usage

Run the main script:
```bash
python main.py
```

This will demonstrate the pipeline with a sample query.

## Architecture

- `src/core/interfaces/`: Abstract interfaces for LLM, embedding, and DB providers
- `src/infra/`: Concrete implementations (adapters)
- `src/app/`: Application logic, registries, factories, pipeline
- `config/`: Settings and logging configuration