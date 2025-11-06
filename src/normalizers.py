# src/normalizers.py
import pandas as pd
from .utils import normalize_case_id, normalize_parcel, coerce_dates, raw_row_hash

def normalize_oakland_boca(df: pd.DataFrame, city: str) -> pd.DataFrame:
    rename_map = {
        "Case #": "case_id_raw",
        "Main Address": "address_raw",
        "Parcel": "parcel_raw",
        "Opened Date": "opened_date",
        "Closed Date": "closed_date",
        "Case Type": "case_type",
        "Case Status": "case_status",
        "Project": "project",
        "District": "district",
        "Assigned To": "assigned_to",
        "Violation": "violation",
        "Violation Status": "violation_status",
        "Citation Issued": "citation_issued",
        "Compliance Date": "compliance_date",
        "Resolved Date": "resolved_date",
        "Violation Fee Total": "fee_total",
        "Description": "description",
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["case_id"] = df2.get("case_id_raw").apply(normalize_case_id) if "case_id_raw" in df2 else None
    df2["parcel_norm"] = df2.get("parcel_raw").apply(normalize_parcel) if "parcel_raw" in df2 else None
    df2["city"] = city

    cols = [
        "case_id","case_id_raw",
        "parcel_norm","parcel_raw",
        "city","address_raw",
        "opened_date","closed_date",
        "case_type","case_status","project","district","assigned_to",
        "violation","violation_status","citation_issued","compliance_date","resolved_date",
        "fee_total","description"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_pompano(df: pd.DataFrame, city: str) -> pd.DataFrame:
    rename_map = {
        "Formatted Case Number": "case_id_raw",
        "Address": "address_raw",
        "Violation Code": "violation_code",
        "Violation Description": "violation",
        "Case Disposition": "disposition",
        "Case Status Description": "case_status",
        "Case Established Date": "opened_date",
        "Days Active": "days_active",
        "Last Action": "last_action",
        "Result Date": "result_date",
        "Next Action": "next_action",
        "Due Date": "due_date",
        "Parcel": "parcel_raw",  # just in case some exports include it
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["case_id"] = df2.get("case_id_raw").apply(normalize_case_id) if "case_id_raw" in df2 else None
    df2["parcel_norm"] = df2.get("parcel_raw").apply(normalize_parcel) if "parcel_raw" in df2 else None
    df2["city"] = city

    cols = [
        "case_id","case_id_raw",
        "parcel_norm","parcel_raw",
        "city","address_raw",
        "opened_date","result_date","due_date","days_active",
        "case_status","disposition","violation_code","violation",
        "last_action","next_action"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    if "days_active" in out.columns:
        out["days_active"] = pd.to_numeric(out["days_active"], errors="coerce")
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_wilton(df: pd.DataFrame, city: str) -> pd.DataFrame:
    rename_map = {
        "File#": "case_id_raw",
        "Address": "address_raw",
        "Violation": "violation",
        "Open Date": "opened_date",
        "Status": "case_status",
        "Parcel": "parcel_raw",  # if present
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["case_id"] = df2.get("case_id_raw").apply(normalize_case_id) if "case_id_raw" in df2 else None
    df2["parcel_norm"] = df2.get("parcel_raw").apply(normalize_parcel) if "parcel_raw" in df2 else None
    df2["city"] = city

    cols = [
        "case_id","case_id_raw",
        "parcel_norm","parcel_raw",
        "city","address_raw",
        "opened_date","case_status","violation"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_any(df: pd.DataFrame, city: str) -> pd.DataFrame:
    cols = set([c.lower() for c in df.columns])
    if "formatted case number" in cols or "case status description" in cols:
        return normalize_pompano(df, city)
    if "file#" in cols and "violation" in cols:
        return normalize_wilton(df, city)
    return normalize_oakland_boca(df, city)
