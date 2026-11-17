from typing import TypedDict
import os
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


class AnalystState(TypedDict):
    question: str
    data_summary: str
    api_key: str
    answer: str


def _get_llm(api_key: str):
    """Create the Groq chat model using the supplied key or .env setting."""
    key = api_key or os.getenv("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY missing. Add it to your .env file.")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
        api_key=key,
    )


def analyst_node(state: AnalystState):
    """Single LangGraph node: analyze the user's question against data context."""
    llm = _get_llm(state.get("api_key", ""))
    messages = [
        SystemMessage(content=(
            "You are DataMind AI, a careful data analyst. Use the supplied dataset "
            "context, explain your reasoning clearly, and never invent unavailable values."
        )),
        HumanMessage(content=(
            f"Dataset context:\n{state['data_summary']}\n\n"
            f"User question: {state['question']}"
        )),
    ]
    response = llm.invoke(messages)
    return {"answer": response.content}


# Beginner-friendly LangGraph: START -> analyst -> END
workflow = StateGraph(AnalystState)
workflow.add_node("analyst", analyst_node)
workflow.add_edge(START, "analyst")
workflow.add_edge("analyst", END)
analyst_graph = workflow.compile()


def _dataset_summary(df: pd.DataFrame) -> str:
    return (
        f"Rows: {len(df)}\n"
        f"Columns: {len(df.columns)}\n"
        f"Column names: {list(df.columns)}\n"
        f"Data types:\n{df.dtypes.to_string()}\n"
        f"Statistics:\n{df.describe(include='all').transpose().head(30).to_string()}\n"
        f"Sample rows:\n{df.head(10).to_string(index=False)}"
    )


def ask_data_agent(df: pd.DataFrame, question: str, api_key: str = "") -> str:
    """Compatibility function used by app.py; runs the simple LangGraph."""
    result = analyst_graph.invoke({
        "question": question,
        "data_summary": _dataset_summary(df),
        "api_key": api_key,
        "answer": "",
    })
    return result["answer"]


def ask_analyst(question: str, df: pd.DataFrame) -> str:
    """Convenience wrapper for callers that keep the API key in environment."""
    return ask_data_agent(df, question, os.getenv("GROQ_API_KEY", ""))


def generate_sql(df: pd.DataFrame, question: str, api_key: str = "") -> str:
    """Generate one read-only SQLite SELECT query for the uploaded dataframe."""
    columns = "\n".join(f"- {col} ({df[col].dtype})" for col in df.columns)
    prompt = f"""Create one SQLite query for this user's data question.
Table name: data
Available columns and types:
{columns}
Question: {question}

Rules:
- Return SQL only, with no markdown fences or explanation.
- Generate exactly one SELECT query.
- Use only the table named data and the listed columns.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multiple statements.
- Quote column names with double quotes if they contain spaces or special characters.
- Add a reasonable LIMIT (maximum 200) unless the query is an aggregate.
"""
    response = _get_llm(api_key).invoke([
        SystemMessage(content="You generate safe, read-only SQLite SQL."),
        HumanMessage(content=prompt),
    ])
    sql = str(response.content).strip()
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    return sql.strip()
