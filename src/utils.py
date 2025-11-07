# src/utils.py
import re
import json
import hashlib
import pandas as pd

DATE_COLS = [
    "opened_date", "closed_date",
    "citation_issued", "compliance_date", "resolved_date",
    "result_date", "due_date"
]

def normalize_case_id(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip().replace(" ", "").replace("-", "")
    return v or None

def normalize_parcel(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    digits = re.sub(r"[^0-9]", "", value)
    return digits or None

def coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in DATE_COLS:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce").dt.date
    return out

def raw_row_hash(row: pd.Series) -> str:
    # Stable hash for de-duplication; tweak the subset as you prefer
    subset = {
        "case_id": row.get("case_id"),
        "case_id_raw": row.get("case_id_raw"),
        "parcel_norm": row.get("parcel_norm"),
        "address_raw": row.get("address_raw"),
        "opened_date": str(row.get("opened_date")),
        "city": row.get("city"),
    }
    j = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.md5(j.encode("utf-8")).hexdigest()

# -------------------------------------------------------------------
# Make ADE SDK objects JSON-serializable (Chunks, Splits, Metadata)
# -------------------------------------------------------------------
from typing import Any

def to_jsonable(x: Any):
    """
    Recursively convert ADE SDK objects (Chunk, Split, Metadata, etc.)
    into plain Python types so they can be safely json.dump'ed.
    """
    # Primitive types
    if x is None or isinstance(x, (str, int, float, bool)):
        return x

    # Dict → dict
    if isinstance(x, dict):
        return {k: to_jsonable(v) for k, v in x.items()}

    # Lists / tuples / sets → list
    if isinstance(x, (list, tuple, set)):
        return [to_jsonable(v) for v in x]

    # Pydantic v2 models (ADE uses them)
    if hasattr(x, "model_dump"):      # LandingAI objects use this
        try:
            return to_jsonable(x.model_dump())
        except Exception:
            pass

    # Generic object → try __dict__
    if hasattr(x, "__dict__"):
        try:
            return to_jsonable(vars(x))
        except Exception:
            pass

    # Last fallback → string
    return str(x)
