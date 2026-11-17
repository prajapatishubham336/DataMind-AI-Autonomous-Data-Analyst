# DataMind AI — Autonomous Data Analyst

## Features
- Upload CSV and Excel datasets
- Dataset KPIs, preview, column profile and charts
- Groq-powered AI Analyst using a simple LangGraph flow
- SQL workspace for read-only SELECT/WITH queries
- Data cleaning and downloadable PDF/profile reports

## Windows setup (PowerShell)

```powershell
cd DataMind_AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your Groq key:

```env
GROQ_API_KEY=your_actual_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Run:

```powershell
streamlit run app.py
```

## LangGraph flow
The code is intentionally simple and notebook-friendly:
1. Define `AnalystState`
2. Write one `analyst_node`
3. Create `StateGraph`
4. Connect `START -> analyst -> END`
5. Compile and invoke

A beginner notebook is included at `notebooks/LangGraph_Basics.ipynb`.

## Notes
- Groq calls need internet and a valid API key. Rate limits depend on your account/model.
- SQL runs against an in-memory SQLite copy of the uploaded dataset.
- This is a learning/portfolio project, not a production-hardened service.
