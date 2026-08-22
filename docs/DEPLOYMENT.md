# Deployment & Hosting Guide

This guide covers deployment options for the **NLP-SQL Federated Engine**, from automated GitHub CI/CD to Docker and local hosting.

---

## 1. Hugging Face Spaces with Automated GitHub CI/CD (100% Free)

### Step 1: Create a Space on Hugging Face
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set Space Name: `nlp-sql-engine`.
3. Select **Gradio** as SDK and template **Blank**.
4. Hardware: Select **ZeroGPU (Free)**.
5. Click **Create Space**.

### Step 2: Set Secrets on Hugging Face
In your Space ➜ **Settings** ➜ **Variables and secrets** ➜ **New secret**:

| Key | Description |
| :--- | :--- |
| `OPENAI_API_KEY` | OpenRouter API Key (`sk-or-v1-...`) |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` |
| `GEMINI_API_KEY` | Google AI Studio Key (`AIzaSy...`) |
| `EMBEDDING_PROVIDER` | `gemini` |
| `PLANNER_LLM_PROVIDER` | `openrouter` |
| `GENERATION_LLM_PROVIDER` | `openrouter` |
| `DEBUG_LLM_PROVIDER` | `openrouter` |

### Step 3: Configure GitHub Actions Auto-Deploy
1. Get a Hugging Face write token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. On your GitHub Repository ➜ **Settings** ➜ **Secrets and variables** ➜ **Actions** ➜ **New repository secret**:
   - Name: `HF_TOKEN`
   - Value: Your Hugging Face write token (`hf_...`).
3. Every `git push origin main` will automatically build and deploy to your live Hugging Face Space!

---

## 2. Docker Compose (Local Production Container)

### Build & Run
```bash
# 1. First-time build & run
docker compose up --build

# 2. Everyday instant start (0.5s boot, zero re-downloads)
docker compose up

# 3. Stop container
docker compose down
```

Access the endpoints:
- **Interactive Web Dashboard**: `http://localhost:8000`
- **Swagger REST API**: `http://localhost:8000/docs`
- **Healthcheck**: `http://localhost:8000/health`

---

## 3. Render.com (100% Free Web Service)

1. Create a new **Web Service** on [Render.com](https://dashboard.render.com).
2. Connect your GitHub repository.
3. Configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python scripts/setup_db.py`
   - **Start Command**: `uvicorn nlp_sql_engine.web.app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Add your `.env` variables under **Environment Variables** and click **Deploy**.
