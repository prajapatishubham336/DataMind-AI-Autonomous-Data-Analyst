# DataMind-AI-Autonomous-Data-Analyst
An AI-powered Autonomous Data Analyst built with Python, Streamlit, LangGraph, and Groq. Upload CSV or Excel datasets, explore data, generate interactive visualizations, ask natural-language questions, generate read-only SQL queries, clean datasets, and create PDF reports.


# 🧠 DataMind AI – Autonomous Data Analyst

### Transform Raw Data into Actionable Intelligence with AI.

<p align="center">
  An AI-powered data analytics application that helps users explore datasets, generate insights, interact with data using natural language, generate SQL queries, and create analytical reports.
</p>

---

## 📌 Overview

**DataMind AI** is an AI-powered Autonomous Data Analyst built using Python, Streamlit, LangGraph, and Groq.

The application allows users to upload CSV and Excel datasets and perform data analysis through an interactive dashboard.

Instead of manually exploring every column, users can visualize data, identify missing values, clean datasets, ask questions in natural language, generate SQL queries, and export reports.

The project combines traditional data analytics with Generative AI to make data exploration easier and more accessible.

### 📚 Core Libraries & Documentation

| Library / Technology | Purpose | Official Documentation |
|---|---|---|
| Python | Core programming language | [Documentation](https://docs.python.org/3/) |
| Streamlit | Interactive dashboard | [Documentation](https://docs.streamlit.io/) |
| Pandas | Data manipulation and analysis | [Documentation](https://pandas.pydata.org/docs/) |
| NumPy | Numerical computing | [Documentation](https://numpy.org/doc/) |
| Plotly | Interactive data visualization | [Documentation](https://plotly.com/python/) |
| LangChain | LLM integration | [Documentation](https://python.langchain.com/docs/introduction/) |
| LangGraph | Agent workflow orchestration | [Documentation](https://docs.langchain.com/oss/python/langgraph/overview) |
| Groq | LLM inference API | [Documentation](https://console.groq.com/docs/overview) |
| SQLite | Lightweight SQL database | [Documentation](https://www.sqlite.org/docs.html) |
| ReportLab | PDF report generation | [Documentation](https://docs.reportlab.com/) |
| OpenPyXL | Excel file processing | [Documentation](https://openpyxl.readthedocs.io/) |

---

## ✨ Key Features

### 📊 1. Interactive Analytics Dashboard
- Dataset overview and statistics.
- Total rows and columns.
- Missing value detection.
- Duplicate row detection.
- Dataset preview.
- Column-wise data profiling.

### 📂 2. Data Upload & Exploration
- Upload CSV datasets.
- Upload Excel datasets.
- Explore dataset structure.
- Generate interactive charts.
- Download original datasets.

### 🤖 3. AI Data Analyst
- Ask questions about datasets using natural language.
- Get AI-generated analytical explanations.
- Powered by Groq LLM.
- Simple LangGraph-based analyst workflow.

### 🗃️ 4. Natural Language to SQL Agent
- Convert natural language questions into SQL queries.
- Generate SQLite-compatible SQL.
- Review and edit generated queries.
- Execute read-only SQL queries.
- Download query results.

### 🧹 5. Data Cleaning
- Detect missing values.
- Remove duplicate records.
- Drop rows containing missing values.
- Fill numerical missing values using median.
- Fill categorical missing values using mode.
- Download cleaned datasets.

### 📈 6. Insights & Reports
- Automatic dataset insights.
- Numerical column statistics.
- Dataset profiling report.
- Generate downloadable PDF reports.
- Export column profiles as CSV.

---

## 🏗️ System Architecture

```text
                 USER
                  |
                  v
          STREAMLIT DASHBOARD
                  |
                  v
          DATA UPLOAD (CSV/XLSX)
                  |
                  v
          PANDAS DATA PROCESSING
                  |
          +-------+--------+
          |       |        |
          v       v        v
       PROFILE  CLEANING  VISUALIZATION
          |       |        |
          +-------+--------+
                  |
          +-------+--------+
          |                |
          v                v
      AI ANALYST         SQL AGENT
          |                |
          v                v
       LANGGRAPH          SQLITE
          |
          v
       GROQ LLM
          |
          v
     AI-GENERATED ANSWERS

                  |
                  v
             PDF REPORT
```

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| LLM Provider | Groq |
| LLM Integration | LangChain |
| Agent Framework | LangGraph |
| SQL Engine | SQLite |
| PDF Generation | ReportLab |
| Configuration | python-dotenv |

---

## 📁 Project Structure

```text
DataMind-AI-Autonomous-Data-Analyst/
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
├── .env.example
│
├── .gitignore
│
├── sample_sales.csv
│
├── .streamlit/
│   └── config.toml
│
└── datamind/
    │
    ├── __init__.py
    │
    ├── agents.py
    │
    ├── data_tools.py
    │
    └── reports.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/prajapatishubham336/DataMind-AI-Autonomous-Data-Analyst.git
```

### 2. Navigate to Project Directory

```bash
cd DataMind-AI-Autonomous-Data-Analyst
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Groq API Key

Create a `.env` file in the root directory.

```env
GROQ_API_KEY=your_groq_api_key
```

Get your API key from:

https://console.groq.com/keys

### 7. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

Usually:

```text
http://localhost:8501
```

---

## 🚀 Application Workflow

1. Launch the Streamlit application.
2. Upload a CSV or Excel dataset.
3. Explore dataset statistics and visualizations.
4. Ask questions using the AI Analyst.
5. Generate SQL queries using natural language.
6. Clean missing and duplicate values.
7. Generate insights and download PDF reports.

---

## 🔐 Security & Data Handling

- API keys are stored in environment variables.
- `.env` should never be committed to GitHub.
- SQL execution is restricted to read-only queries.
- Uploaded datasets are processed locally by the application.
- Dataset schema and sample rows are sent to Groq when using the AI Analyst.

**Important:** Do not upload confidential or sensitive datasets unless you are authorized to share them.

---

## ⚠️ Current Limitations

- AI analysis uses the dataset schema and sample rows as context; it does not independently calculate every requested statistic.
- Groq API availability, model access, and rate limits depend on the provider.
- SQL queries should be reviewed before execution.
- The project is a portfolio implementation and requires additional security and testing before production deployment.

---

## 🔮 Future Enhancements

- Multi-agent analytics workflow.
- Advanced statistical analysis.
- Automated anomaly detection.
- Predictive analytics and machine learning.
- Database connectivity.
- Advanced AI-generated visualizations.
- User authentication and role-based access.
- Cloud deployment.
- Automated data quality evaluation.

---

## 👨‍💻 Author

**Shubham Prajapati**

AI / ML Engineer | Data Science | Generative AI | Agentic AI

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.

---

### Turning Data into Decisions with AI. 🚀
