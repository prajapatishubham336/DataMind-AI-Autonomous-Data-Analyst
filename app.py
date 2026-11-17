import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from datamind.data_tools import (
    profile_dataframe,
    clean_dataframe,
    dataframe_to_sqlite,
    run_readonly_sql
)

from datamind.agents import ask_data_agent, generate_sql
from datamind.reports import make_pdf_report


# 1. CONFIGURATION
load_dotenv()
st.set_page_config(
    page_title="DataMind AI | Autonomous Data Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM CSS
st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #0b1020;
    color: #e8edf8;
}

/* Remove white header */
header[data-testid="stHeader"] {
    background: #0b1020 !important;
    height: 2.8rem;
}

[data-testid="stDecoration"] {
    display: none;
}

/* Main content */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #10182b;
    border-right: 1px solid #263653;
}

[data-testid="stSidebar"] * {
    color: #dce6fa;
}

[data-testid="stSidebar"] label {
    color: #aab8d2 !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #f4f7ff !important;
}

/* Hero */
.hero {
    padding: 25px 30px;
    border: 1px solid #273653;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #172746,
        #111a30 65%,
        #1b2340
    );
    margin-bottom: 25px;
}

.hero h1 {
    color: #ffffff !important;
    font-size: 2.1rem;
    margin: 0;
}

.hero p {
    color: #aab8d2;
    margin-top: 8px;
}

/* Metric cards */
.metric {
    background: linear-gradient(145deg, #17233b, #111a2d);
    border: 1px solid #273653;
    padding: 20px;
    border-radius: 15px;
    min-height: 105px;
}

.metric-label {
    color: #9eacc6;
    font-size: 0.9rem;
}

.metric-value {
    color: #ffffff;
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 8px;
}

/* Section headings */
.section {
    color: #f3f6ff;
    font-weight: 700;
    font-size: 1.2rem;
    margin: 22px 0 12px;
}

/* Buttons */
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #40547a;
    min-height: 2.6rem;
    background: #172746;
    color: white;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    border-color: #7188ff;
    color: white;
}

div.stButton > button[kind="primary"] {
    background: #536dfe;
    border: none;
    color: white;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background-color: #17233b !important;
    color: white !important;
    border: 1px solid #344766 !important;
    border-radius: 9px !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    background-color: #17233b;
    border-radius: 9px;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #273653;
    border-radius: 10px;
    overflow: hidden;
}

/* Alerts */
.stAlert {
    border-radius: 10px;
}

/* Captions */
.small-note {
    color: #9eacc6;
    font-size: 0.85rem;
}

/* Divider */
hr {
    border-color: #263653;
}

/* Download buttons */
.stDownloadButton button {
    background: #172746;
    color: white;
    border: 1px solid #40547a;
    border-radius: 9px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #121d33;
    border: 1px solid #273653;
    border-radius: 12px;
    padding: 12px;
}

/* Responsive */
@media (max-width: 768px) {
    .hero {
        padding: 18px;
    }

    .hero h1 {
        font-size: 1.6rem;
    }

    .metric {
        margin-bottom: 10px;
    }
}

</style>
""", unsafe_allow_html=True)

# 3. SESSION STATE
if "df" not in st.session_state:
    st.session_state.df = None

if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "last_profile" not in st.session_state:
    st.session_state.last_profile = None

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

# 4. SIDEBAR
with st.sidebar:
    st.markdown("## 🧠 DataMind AI")
    st.caption("Autonomous Data Analyst")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Upload & Explore",
            "Ask AI Analyst",
            "SQL Agent",
            "Data Cleaning",
            "Insights & Reports"
        ],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("### Created by")
    st.markdown("**Shubham Prajapati**")
    st.caption("Python • Streamlit • LangGraph • Groq")
    st.markdown("---")
    if st.button("↻ Reset workspace", use_container_width=True):

        st.session_state.df = None
        st.session_state.cleaned_df = None
        st.session_state.chat = []
        st.session_state.last_profile = None
        st.session_state.generated_sql = ""
        st.rerun()

    st.markdown("---")
    st.markdown("### Quick Upload")
    uploaded = st.file_uploader(
        "Upload CSV / Excel",
        type=["csv", "xlsx", "xls"],
        key="quick_upload"
    )

    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded)
            else:
                st.session_state.df = pd.read_excel(uploaded)
            st.session_state.cleaned_df = None
            st.success(f"Loaded: {uploaded.name}")
        except Exception as e:
            st.error(f"Could not read file: {e}")

# 5. COMMON FUNCTIONS
df = st.session_state.df
def require_data():
    if st.session_state.df is None:
        st.warning("Please upload a CSV or Excel dataset from the sidebar first.")
        return False
    return True


def style_chart(fig):
    fig.update_layout(
        paper_bgcolor="#0b1020",
        plot_bgcolor="#121d33",
        font=dict(color="#e8edf8"),
        title_font=dict(color="#ffffff", size=18),
        margin=dict(l=25, r=25, t=55,  b=30),
        legend=dict(font=dict(color="#e8edf8")),
        xaxis=dict(
            gridcolor="#263653",
            zerolinecolor="#263653"
        ),

        yaxis=dict(
            gridcolor="#263653",
            zerolinecolor="#263653"
        )
    )
    return fig


# 6. HERO SECTION
st.markdown(
    """
<div class="hero">
<h1>🧠 DataMind AI</h1>
<p>
Turn raw data into clear answers,
interactive visuals and actionable insights.
</p>
<p class="small-note">
Workspace of <b>Shubham Prajapati</b>
· Autonomous Data Analyst
</p>
</div>
""",
    unsafe_allow_html=True
)
# 7. OVERVIEW
if page == "Overview":
    st.subheader("📊 Analytics Overview")
    if not require_data():
        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown("### Start with your dataset")
            st.write(
                "Upload a CSV or Excel file to unlock "
                "AI-powered data analysis."
            )
            st.info("Upload your dataset using the sidebar.")
        with c2:
            st.markdown("### What you can do")
            st.write("""
            📊 Explore data and interactive charts
            💬 Ask questions using AI
            🗃️ Generate SQL queries
            🧹 Clean missing and duplicate values
            🧾 Generate PDF reports
            """)

    else:
        df = st.session_state.df
        profile = profile_dataframe(df)
        st.session_state.last_profile = profile
        # KPI CARDS
        st.markdown(
            '<div class="section">Dataset Statistics</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(4)
        metrics = [
            ("Total Rows", f"{profile['rows']:,}"),
            ("Total Columns", f"{profile['columns']:,}"),
            ("Missing Cells", f"{profile['missing_cells']:,}"),
            ("Duplicate Rows", f"{profile['duplicate_rows']:,}")
        ]

        for col, (label, value) in zip(cols, metrics):
            col.markdown(
                f"""
                <div class="metric">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # DATA PREVIEW
        st.markdown(
            '<div class="section">Dataset Preview</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            df.head(10),
            use_container_width=True,
            height=350
        )

        # COLUMN OVERVIEW
        st.markdown(
            '<div class="section">Column Overview</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            profile["column_summary"],
            use_container_width=True,
            height=350
        )

        # QUICK CHART
        numeric = df.select_dtypes(
            include="number"
        ).columns.tolist()
        if numeric:
            st.markdown(
                '<div class="section">Data Visualization</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns([1, 2])
            with col1:
                selected_column = st.selectbox(
                    "Choose numeric column",
                    numeric
                )

            with col2:
                chart_type = st.selectbox(
                    "Choose chart type",
                    [
                        "Histogram",
                        "Box Plot"
                    ]
                )

            if chart_type == "Histogram":
                fig = px.histogram(
                    df,
                    x=selected_column,
                    title=f"Distribution of {selected_column}",
                    template="plotly_dark"
                )

            else:
                fig = px.box(
                    df,
                    y=selected_column,
                    title=f"Box Plot of {selected_column}",
                    template="plotly_dark"
                )

            fig = style_chart(fig)
            st.plotly_chart(fig, use_container_width=True)


# 8. UPLOAD & EXPLORE
elif page == "Upload & Explore":
    st.subheader("📂 Upload & Explore")
    if require_data():
        df = st.session_state.df
        st.success(
            f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns"
        )

        st.markdown("### Dataset Information")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{df.shape[0]:,}")
        c2.metric("Columns", f"{df.shape[1]:,}")
        c3.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        st.markdown("### Full Dataset")
        st.dataframe(df, use_container_width=True, height=400)
        st.download_button(
            "⬇️ Download Original Dataset",
            df.to_csv(index=False).encode("utf-8"),
            "datamind_dataset.csv",
            "text/csv"
        )

        st.markdown("---")
        st.markdown("### Create Visualization")
        numeric = df.select_dtypes(include="number").columns.tolist()
        categorical = df.select_dtypes(exclude="number").columns.tolist()
        chart_type = st.selectbox("Chart Type",
            [
                "Histogram",
                "Bar Chart",
                "Scatter Plot",
                "Box Plot"
            ]
        )

        if chart_type == "Histogram" and numeric:
            x = st.selectbox("Numeric Column", numeric)
            fig = px.histogram(df, x=x, title=f"Distribution of {x}",
                template="plotly_dark"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        elif chart_type == "Bar Chart" and categorical:
            x = st.selectbox("Category Column",  categorical)
            counts = (
                df[x]
                .astype(str)
                .value_counts()
                .head(20)
                .reset_index()
            )

            counts.columns = [x, "Count"]
            fig = px.bar(counts, x=x,
                y="Count",
                title=f"Count by {x}",
                template="plotly_dark"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        elif chart_type == "Scatter Plot" and len(numeric) >= 2:
            c1, c2 = st.columns(2)
            xcol = c1.selectbox(
                "X Axis",
                numeric,
                key="scatter_x"
            )

            ycol = c2.selectbox(
                "Y Axis",
                [c for c in numeric if c != xcol],
                key="scatter_y"
            )

            fig = px.scatter(
                df,
                x=xcol,
                y=ycol,
                title=f"{xcol} vs {ycol}",
                template="plotly_dark"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        elif chart_type == "Box Plot" and numeric:

            x = st.selectbox(
                "Numeric Column",
                numeric,
                key="box_col"
            )

            fig = px.box(
                df,
                y=x,
                title=f"Box Plot of {x}",
                template="plotly_dark"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        else:

            st.info(
                "This chart requires suitable numeric or categorical columns."
            )

# 9. ASK AI ANALYST
elif page == "Ask AI Analyst":
    st.subheader("💬 Ask AI Analyst")
    st.write("Ask questions about your dataset using natural language.")
    if require_data():
        df = st.session_state.df
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            st.warning("Please configure GROQ_API_KEY in your .env file.")

        # Chat history
        for item in st.session_state.chat:
            with st.chat_message(item["role"]):
                st.markdown(item["content"])
        prompt = st.chat_input("Example: What are the top 5 insights in this dataset?")

        if prompt:
            st.session_state.chat.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your dataset..."):
                    try:
                        answer = ask_data_agent(df, prompt, api_key)
                    except Exception as e:
                        answer = (
                            f"AI request failed: {e}\n\n"
                            "Check your Groq API key, internet connection "
                            "and model quota."
                        )

                    st.markdown(answer)
            st.session_state.chat.append({
                "role": "assistant",
                "content": answer
            })

        if st.button("Clear Chat History"):
            st.session_state.chat = []
            st.rerun()


# 10. SQL AGENT
elif page == "SQL Agent":
    st.subheader("🗃️ SQL Agent")
    st.write("Convert natural language questions into read-only SQL queries.")
    if require_data():
        df = st.session_state.df
        question = st.text_input(
            "What do you want to find?",
            placeholder="Example: Show average sales by region"
        )
        api_key = os.getenv("GROQ_API_KEY", "")
        if st.button(
            "Generate SQL",
            type="primary",
            use_container_width=True
        ):

            if not question.strip():
                st.error("Please enter a question.")
            elif not api_key:
                st.error("Configure GROQ_API_KEY in your .env file.")
            else:
                with st.spinner("Generating SQL..."):
                    try:
                        sql = generate_sql(df, question, api_key)
                        st.session_state.generated_sql = sql
                    except Exception as e:
                        st.error(f"SQL generation failed: {e}")

        sql_text = st.text_area(
            "Review / Edit SQL",
            value=st.session_state.generated_sql,
            height=150
        )

        if st.button(
            "▶ Run Read-only SQL",
            type="primary",
            use_container_width=True
        ):

            try:
                result = run_readonly_sql(df, sql_text)
                st.success("SQL executed successfully.")
                st.dataframe(
                    result,
                    use_container_width=True
                )

                st.download_button(
                    "⬇️ Download Query Result",
                    result.to_csv(index=False).encode("utf-8"),
                    "sql_result.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(str(e))

        st.info(
            "Safety: Only a single SELECT or WITH query is accepted. "
            "Database write operations are blocked."
        )


# 11. DATA CLEANING
elif page == "Data Cleaning":
    st.subheader("🧹 Data Cleaning")
    st.write("Clean missing values and duplicate rows from your dataset.")
    if require_data():
        df = st.session_state.df
        profile = profile_dataframe(df)
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Missing Cells",
            profile["missing_cells"]
        )
        c2.metric(
            "Duplicate Rows",
            profile["duplicate_rows"]
        )

        c3.metric("Total Rows", len(df))
        st.markdown("### Cleaning Options")
        missing_method = st.selectbox(
            "Missing Values Treatment",
            [
                "Keep unchanged",
                "Drop rows with missing values",
                "Fill numeric with median and text with mode"
            ]
        )

        drop_duplicates = st.checkbox(
            "Remove duplicate rows",
            value=True
        )

        if st.button(
            "🧹 Clean Dataset",
            type="primary",
            use_container_width=True
        ):

            try:
                st.session_state.cleaned_df = clean_dataframe(
                    df,
                    missing_method,
                    drop_duplicates
                )

                st.success("Dataset cleaning completed successfully.")
            except Exception as e:
                st.error(f"Cleaning failed: {e}")
        if st.session_state.cleaned_df is not None:
            cleaned = st.session_state.cleaned_df
            st.markdown("### Cleaned Dataset Preview")
            st.success(
                f"Cleaned dataset: {cleaned.shape[0]} rows × "
                f"{cleaned.shape[1]} columns"
            )

            st.dataframe(
                cleaned.head(30),
                use_container_width=True
            )

            st.download_button(
                "⬇️ Download Cleaned CSV",
                cleaned.to_csv(index=False).encode("utf-8"),
                "datamind_cleaned.csv",
                "text/csv"
            )


# 12. INSIGHTS & REPORTS
elif page == "Insights & Reports":
    st.subheader("📈 Insights & Reports")
    st.write("Automatically generate dataset insights and downloadable reports.")
    if require_data():
        df = st.session_state.df
        profile = profile_dataframe(df)
        numeric = df.select_dtypes(
            include="number"
        )
        st.markdown("### Automatic Data Insights")
        insights = [
            f"Dataset contains **{len(df):,} rows** "
            f"and **{len(df.columns)} columns**.",

            f"There are **{profile['missing_cells']:,} missing cells** "
            f"({profile['missing_percent']:.2f}% of all cells).",

            f"Found **{profile['duplicate_rows']:,} duplicate rows**."

        ]

        for col in numeric.columns:
            if numeric[col].notna().any():
                insights.append(
                    f"**{col}**: "
                    f"mean {numeric[col].mean():,.3f}, "
                    f"median {numeric[col].median():,.3f}, "
                    f"min {numeric[col].min():,.3f}, "
                    f"max {numeric[col].max():,.3f}."

                )

        for insight in insights:
            st.markdown(f"- {insight}")
        st.markdown("---")
        st.markdown("### Generate PDF Report")
        if st.button(
            "📄 Generate PDF Report",
            type="primary",
            use_container_width=True
        ):

            try:
                pdf = make_pdf_report(df, profile, insights)
                st.download_button(
                    "⬇️ Download PDF Report",
                    pdf,
                    "datamind_report.pdf",
                    "application/pdf"
                )

            except Exception as e:
                st.error(f"PDF generation failed: {e}")
        st.markdown("---")
        st.markdown("### Download Dataset Profile")
        st.download_button(
            "⬇️ Download Profile CSV",
            profile["column_summary"].to_csv(
                index=False
            ).encode("utf-8"),
            "datamind_profile.csv",
            "text/csv"
        )


# 13. FOOTER
st.markdown("---")
st.markdown(
    """
    <div style="
        text-align:center;
        color:#8292b2;
        padding:12px;
        font-size:13px;
    ">
        🧠 DataMind AI |
        Built by Shubham Prajapati |
        Python • Streamlit • LangGraph • Groq
        <br><br>
        AI-generated outputs should be reviewed before business decisions.
    </div>
    """,
    unsafe_allow_html=True
)
