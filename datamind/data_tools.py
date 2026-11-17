import sqlite3
import re
import pandas as pd

def profile_dataframe(df: pd.DataFrame) -> dict:
    summary = pd.DataFrame({
        "column": df.columns.astype(str),
        "dtype": [str(x) for x in df.dtypes],
        "non_null": [int(df[c].notna().sum()) for c in df.columns],
        "missing": [int(df[c].isna().sum()) for c in df.columns],
        "unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    total = max(int(df.size), 1)
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_percent": float(df.isna().sum().sum() / total * 100),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_summary": summary,
    }

def clean_dataframe(df, missing_method, drop_duplicates=True):
    out = df.copy()
    if missing_method == "Drop rows with missing values":
        out = out.dropna()
    elif missing_method == "Fill numeric with median and text with mode":
        for col in out.columns:
            if pd.api.types.is_numeric_dtype(out[col]):
                if out[col].notna().any():
                    out[col] = out[col].fillna(out[col].median())
            else:
                modes = out[col].mode(dropna=True)
                if not modes.empty:
                    out[col] = out[col].fillna(modes.iloc[0])
    if drop_duplicates:
        out = out.drop_duplicates()
    return out.reset_index(drop=True)

def dataframe_to_sqlite(df):
    conn = sqlite3.connect(":memory:")
    safe = df.copy()
    safe.columns = [re.sub(r"[^A-Za-z0-9_]", "_", str(c)) or f"column_{i}" for i,
                    c in enumerate(safe.columns)]
    safe.to_sql("data", conn, index=False, if_exists="replace")
    return conn

def run_readonly_sql(df, query):
    q = query.strip().rstrip(";")
    if not q:
        raise ValueError("SQL query is empty.")
    if not re.match(r"^(SELECT|WITH)\b", q, flags=re.I):
        raise ValueError("Only SELECT or WITH queries are allowed.")
    if ";" in q:
        raise ValueError("Only one SQL statement is allowed.")
    blocked = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA|VACUUM)\b"
    if re.search(blocked, q, flags=re.I):
        raise ValueError("Write or administrative SQL commands are blocked.")
    conn = dataframe_to_sqlite(df)
    try:
        return pd.read_sql_query(q, conn)
    finally:
        conn.close()
