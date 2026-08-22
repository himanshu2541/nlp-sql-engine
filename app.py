import os
import sys
import time
import pandas as pd
import gradio as gr

# 1. Ensure databases are seeded on startup
from scripts.setup_db import ensure_directory, seed_crm_db, seed_inventory_db, seed_sales_db

db_dir = "test_database"
if not os.path.exists(os.path.join(db_dir, "crm.db")) or not os.path.exists(os.path.join(db_dir, "sales.db")):
    print("Seeding SQLite databases for first run...")
    ensure_directory()
    seed_crm_db()
    seed_inventory_db()
    seed_sales_db()
    print("Databases initialized.")

# 2. Build Engine Application
from nlp_sql_engine.app.container import AppContainer
from nlp_sql_engine.core.domain.models import NLQuery

app_engine = AppContainer.build()


def run_query(user_question: str):
    if not user_question.strip():
        return "-- Please enter a question", pd.DataFrame(), "⚠️ Question cannot be empty."



    start_time = time.perf_counter()
    try:
        results = list(app_engine.execute(NLQuery(question=user_question)))
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if not results:
            return "-- No result generated", pd.DataFrame(), f"❌ No result returned ({elapsed_ms} ms)"

        res = results[0]

        # Conversational / Guardrail Message
        if res.message:
            return "-- Conversational Guardrail Activated", pd.DataFrame(), f"💬 {res.message}"

        # Error
        if res.error:
            sql_text = res.sql_query.query if res.sql_query else "-- SQL Generation Error"
            return sql_text, pd.DataFrame(), f"❌ Error: {res.error} ({elapsed_ms} ms)"

        # Success
        sql_text = res.sql_query.query if res.sql_query else "-- No SQL generated"
        raw_rows = list(res.result.rows) if res.result and res.result.rows else []

        if raw_rows:
            first_row = raw_rows[0]
            if isinstance(first_row, dict):
                df = pd.DataFrame(raw_rows)
            elif isinstance(first_row, (list, tuple)):
                cols = [f"col_{i+1}" for i in range(len(first_row))]
                df = pd.DataFrame(raw_rows, columns=cols)
            else:
                df = pd.DataFrame(raw_rows, columns=["result"])
        else:
            df = pd.DataFrame({"Status": ["(0 rows returned)"]})

        status_info = f"✅ Query executed successfully in {elapsed_ms} ms ({len(raw_rows)} rows)"
        return sql_text, df, status_info

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return "-- Execution Failed", pd.DataFrame(), f"❌ System Error: {str(e)} ({elapsed_ms} ms)"


# 3. Create Modern Gradio Interface
custom_css = """
footer {visibility: hidden}
.gradio-container {max-width: 1100px !important; margin: auto !important;}
"""

sample_examples = [
    ["What products cost more than $100?"],
    ["List customer names and their order IDs."],
    ["Show product names and their average rating."],
    ["List all customers from the USA."],
    ["How many customers are from the UK?"],
    ["Show all orders placed by Alice Smith."],
    ["Find customers who placed more than one order."],
    ["Hello"],
]

with gr.Blocks(title="NLP-SQL Engine") as demo:
    gr.Markdown(
        """
        # ⚡ NLP-SQL Federated Engine
        ### Natural Language to Multi-Database SQL with Semantic Vector Routing & Self-Correction
        """
    )

    with gr.Row():
        with gr.Column(scale=5):
            query_input = gr.Textbox(
                label="Ask a database question in Natural Language",
                placeholder="e.g. List customer names and their order IDs...",
                lines=2,
            )
            with gr.Row():
                clear_btn = gr.Button("Clear", variant="secondary", size="sm")
                submit_btn = gr.Button("Execute Query 🚀", variant="primary", size="sm")

            gr.Examples(
                examples=sample_examples,
                inputs=[query_input],
                label="💡 Click any sample question to test:",
            )

            with gr.Accordion("🗄️ Connected Databases Schema", open=False):
                gr.Markdown(
                    """
                    - **crm.db**: `customers` (id, name, email, country, signup_date), `reviews` (id, product_id, customer_id, rating, review_text, review_date)
                    - **inventory.db**: `products` (id, product_name, category_id, supplier_id, price, stock_quantity), `categories`, `suppliers`
                    - **sales.db**: `orders` (id, customer_id, order_date, total_amount, status), `order_items`, `payments`
                    """
                )

        with gr.Column(scale=6):
            status_output = gr.Markdown("### Ready to accept questions.")
            sql_output = gr.Code(label="Generated SQL Query", language="sql", lines=4)
            table_output = gr.DataFrame(label="Query Results Data", interactive=False)

    submit_btn.click(
        fn=run_query,
        inputs=[query_input],
        outputs=[sql_output, table_output, status_output],
    )
    query_input.submit(
        fn=run_query,
        inputs=[query_input],
        outputs=[sql_output, table_output, status_output],
    )
    clear_btn.click(
        fn=lambda: ("", "-- Enter a question", pd.DataFrame(), "Ready to accept questions."),
        outputs=[query_input, sql_output, table_output, status_output],
    )

# Launch Gradio interface (disable experimental Node.js SSR proxy)
demo.launch(ssr_mode=False)



