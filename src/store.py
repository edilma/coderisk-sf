#load/save master

from pathlib import Path
import pandas as pd
from .config import RESULTS_DIR, MASTER_PARQUET, MASTER_CSV

def load_master() -> pd.DataFrame:
    if MASTER_PARQUET.exists():
        return pd.read_parquet(MASTER_PARQUET)
    cols = ["violation_type","case_number","case_status","address","opened_date","closed_date",
            "project","district","parcel","assigned_to","zip","city","zone","source_file"]
    return pd.DataFrame(columns=cols)

def save_master(df: pd.DataFrame):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(MASTER_PARQUET, index=False)
    df.to_csv(MASTER_CSV, index=False)
