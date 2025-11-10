# src/normalizers.py
import pandas as pd
from .utils import normalize_case_id, normalize_parcel, coerce_dates, raw_row_hash

# Shared implementation for cities with identical schemas
def _normalize_standard_ade_format(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    """Shared logic for cities using the standard ADE format (currently Oakland Park & Boca Raton)"""
    rename_map = {
        "Case #": "violation_id_raw",
        "Case Type": "violation_type_raw",
        "Case Status": "case_status_raw",
        "Project": "project_raw",
        "District": "district_raw",
        "Main Address": "address_raw",
        "Parcel": "parcel_number_raw",
        "Assigned To": "assigned_to_raw",
        "Opened Date": "opened_date_raw",
        "Closed Date": "closed_date_raw",
        "Violation": "raw_violation",
        "Violation Status": "raw_violation_status",
        "Citation Issued": "citation_issued_raw",
        "Compliance Date": "compliance_date_raw",
        "Resolved Date": "resolved_date_raw",
        "Violation Fee Total": "fee_total_raw"
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["violation_id"] = df2.get("violation_id_raw").apply(normalize_case_id) if "violation_id_raw" in df2 else None
    df2["parcel_number"] = df2.get("parcel_number_raw").apply(normalize_parcel) if "parcel_number_raw" in df2 else None
    df2["city"] = city
    df2["source_file"] = source_file

    cols = [
        "violation_id","violation_id_raw",
        "parcel_number","parcel_number_raw",
        "city","source_file","address_raw",
        "opened_date_raw","closed_date_raw",
        "violation_type_raw","case_status_raw","project_raw","district_raw","assigned_to_raw",
        "raw_violation","raw_violation_status","citation_issued_raw","compliance_date_raw","resolved_date_raw",
        "fee_total_raw"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_oakland(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    """Oakland Park specific normalizer - currently uses standard format"""
    return _normalize_standard_ade_format(df, city, source_file)

def normalize_boca(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    """Boca Raton specific normalizer - handles fixed multi-level headers"""
    
    # Extended rename map for Boca Raton after header fixes
    rename_map = {
        # Standard format (if headers are clean)
        "Case #": "violation_id_raw",
        "Case Type": "violation_type_raw",
        "Case Status": "case_status_raw",
        "Project": "project_raw",
        "District": "district_raw",
        "Main Address": "address_raw",
        "Parcel": "parcel_number_raw",
        "Assigned To": "assigned_to_raw",
        "Opened Date": "opened_date_raw",
        "Closed Date": "closed_date_raw",
        "Violation": "raw_violation",
        "Violation Status": "raw_violation_status",
        "Citation Issued": "citation_issued_raw",
        "Compliance Date": "compliance_date_raw",
        "Resolved Date": "resolved_date_raw",
        "Violation Fee Total": "fee_total_raw",
        
        # Potential variations after header cleaning
        "Case Number": "violation_id_raw",
        "Address": "address_raw",
        "Parcel Number": "parcel_number_raw",
        "Date Opened": "opened_date_raw",
        "Date Closed": "closed_date_raw",
        "Fee Total": "fee_total_raw",
        "Status": "case_status_raw",
    }
    
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["violation_id"] = df2.get("violation_id_raw").apply(normalize_case_id) if "violation_id_raw" in df2 else None
    df2["parcel_number"] = df2.get("parcel_number_raw").apply(normalize_parcel) if "parcel_number_raw" in df2 else None
    df2["city"] = city
    df2["source_file"] = source_file

    cols = [
        "violation_id","violation_id_raw",
        "parcel_number","parcel_number_raw",
        "city","source_file","address_raw",
        "opened_date_raw","closed_date_raw",
        "violation_type_raw","case_status_raw","project_raw","district_raw","assigned_to_raw",
        "raw_violation","raw_violation_status","citation_issued_raw","compliance_date_raw","resolved_date_raw",
        "fee_total_raw"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_pompano(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    # NOTE: Pompano PDFs do not include parcel numbers - parcel_number will be None
    rename_map = {
        "Formatted Case Number": "violation_id_raw",
        "Address": "address_raw",
        "Violation Code": "violation_code_raw",
        "Violation Description": "violation_description_raw",
        "Case Disposition": "case_disposition_raw",
        "Case Status Description": "case_status_raw",
        "Case Established Date": "opened_date_raw",
        "Days Active": "days_active_raw",
        "Last Action": "last_action_raw",
        "Result Date": "result_date_raw",
        "Next Action": "next_action_raw",
        "Due Date": "due_date_raw"
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["violation_id"] = df2.get("violation_id_raw").apply(normalize_case_id) if "violation_id_raw" in df2 else None
    df2["parcel_number"] = df2.get("parcel_number_raw").apply(normalize_parcel) if "parcel_number_raw" in df2 else None
    df2["city"] = city
    df2["source_file"] = source_file

    cols = [
        "violation_id","violation_id_raw",
        "parcel_number","parcel_number_raw",
        "city","source_file","address_raw",
        "opened_date_raw","result_date_raw","due_date_raw","days_active_raw",
        "case_status_raw","case_disposition_raw","violation_code_raw","violation_description_raw",
        "last_action_raw","next_action_raw"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    if "days_active" in out.columns:
        out["days_active"] = pd.to_numeric(out["days_active"], errors="coerce")
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_wilton(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    # NOTE: Wilton Manor PDFs do not include parcel numbers - parcel_number will be None
    rename_map = {
        "File#": "violation_id_raw",
        "Address": "address_raw",
        "Violation": "violation_description_raw",
        "Open Date": "opened_date_raw",
        "Status": "case_status_raw"
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["violation_id"] = df2.get("violation_id_raw").apply(normalize_case_id) if "violation_id_raw" in df2 else None
    df2["parcel_number"] = df2.get("parcel_number_raw").apply(normalize_parcel) if "parcel_number_raw" in df2 else None
    df2["city"] = city
    df2["source_file"] = source_file

    cols = [
        "violation_id","violation_id_raw",
        "parcel_number","parcel_number_raw",
        "city","source_file","address_raw",
        "opened_date_raw","case_status_raw","violation_description_raw"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out

def normalize_margate(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    # NOTE: Margate PDFs do not include parcel numbers - parcel_number will be None
    rename_map = {
        "CASE NUMBER": "violation_id_raw",
        "CASE TYPE ADDRESS": "violation_description_address_raw",
        "STATUS": "case_status_raw",
        "DATE OPENED DAYS ACTIVE": "date_opened_days_active_raw",
        "LAST ACTION NEXT ACTION": "last_next_action_raw",
        "RESULT DATE DUE DATE": "result_due_date_raw",
    }
    df2 = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}).copy()
    df2["violation_id"] = df2.get("violation_id_raw").apply(normalize_case_id) if "violation_id_raw" in df2 else None
    df2["parcel_number"] = df2.get("parcel_number_raw").apply(normalize_parcel) if "parcel_number_raw" in df2 else None
    df2["city"] = city
    df2["source_file"] = source_file

    cols = [
        "violation_id","violation_id_raw",
        "parcel_number","parcel_number_raw",
        "city","source_file","violation_description_address_raw",
        "case_status_raw","date_opened_days_active_raw","last_next_action_raw","result_due_date_raw"
    ]
    out = df2[[c for c in cols if c in df2.columns]].copy()
    out = coerce_dates(out)
    out["raw_row_hash"] = out.apply(raw_row_hash, axis=1)
    return out





def normalize_generic(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    """Generic fallback normalizer - attempts to auto-detect schema"""
    cols = set([c.lower() for c in df.columns])
    if "formatted case number" in cols or "case status description" in cols:
        return normalize_pompano(df, city, source_file)
    if "file#" in cols and "violation" in cols:
        return normalize_wilton(df, city, source_file)
    return _normalize_standard_ade_format(df, city, source_file)

def normalize_any(df: pd.DataFrame, city: str, source_file: str = None) -> pd.DataFrame:
    """Alias for backward compatibility"""
    return normalize_generic(df, city, source_file)
