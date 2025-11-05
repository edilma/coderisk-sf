#for normalization 
import re, pandas as pd

TYPE_MAP = {"fire":"Fire","plumbing":"Plumbing","hvac":"HVAC","electrical":"Electrical","structural":"Structural"}

def infer_zip(addr: str | float):
    if not isinstance(addr, str): return None
    m = re.search(r"\b(\d{5})(?:-\d{4})?\b", addr)
    return m.group(1) if m else None

def normalize_cases(df: pd.DataFrame, default_city: str | None = None) -> pd.DataFrame:
    out = df.copy()
    cmap = {
        "Case Type":"violation_type","Case Number":"case_number","Case Status":"case_status",
        "Main Address":"address","Opened Date":"opened_date","Closed Date":"closed_date",
        "Project":"project","District":"district","Parcel":"parcel","Assigned To":"assigned_to",
        "source_file":"source_file"
    }
    out = out.rename(columns={k:v for k,v in cmap.items() if k in out.columns})
    if "violation_type" in out:
        out["violation_type"] = out["violation_type"].astype(str).str.lower().map(TYPE_MAP).fillna(out["violation_type"])
    out["zip"]  = out["address"].apply(infer_zip) if "address" in out else None
    out["city"] = default_city if default_city else (
        out["address"].str.extract(r",\s*([A-Za-z\s]+),\s*FL\b", expand=False) if "address" in out else None
    )
    out["zone"] = out["zip"].fillna(out.get("city"))
    return out
