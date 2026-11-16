from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
DB_PATH = BASE_DIR / 'data/olist.db'

monthly_sql = (SQL_DIR / "monthly_sales.sql").read_text(encoding="utf-8")

category_sql = (SQL_DIR / 'category_sales.sql').read_text(encoding='utf-8')

geographic_sql = (SQL_DIR / 'geographic_sales.sql').read_text(encoding='utf-8')


@st.cache_data
def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        sales_df = pd.read_sql_query(monthly_sql, conn)
        category_df = pd.read_sql_query(category_sql, conn)
        geo_df = pd.read_sql_query(geographic_sql, conn)
    return sales_df, category_df, geo_df
