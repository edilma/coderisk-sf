# src/db.py
import sqlite3
import pandas as pd
from .config import DB_PATH

def write_cases(df: pd.DataFrame, if_exists: str = "replace"):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        df.to_sql("cases", con, if_exists=if_exists, index=False)

def query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql(sql, con)
