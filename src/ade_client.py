# src/ade_client.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Tuple
import io
import json
import pandas as pd

from landingai_ade import LandingAIADE
from .config import ADE_API_KEY, ADE_MODEL, INTERIM_DIR, RAW_JSON_DIR
from .utils import to_jsonable # <-- relative import

try:
    import markdown as mdlib
except Exception:
    mdlib = None

# ---------- Utilities ----------

def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def response_to_dict(resp) -> dict:
    """
    The SDK returns an object with attributes (markdown, chunks, splits, metadata, grounding).
    Convert to a plain dict so we can serialize reliably.
    """
    if isinstance(resp, dict):
        return resp
    out = {}
    for k in ("markdown", "chunks", "splits", "metadata", "grounding"):
        v = getattr(resp, k, None)
        if v is not None:
            out[k] = v
    return out

def _client() -> LandingAIADE:
    if not ADE_API_KEY:
        raise RuntimeError("VISION_AGENT_API_KEY (or ADE_API_KEY) not set in .env")
    return LandingAIADE(apikey=ADE_API_KEY)

# ---------- ADE parse and table extraction ----------

def parse_pdf(pdf_path: Path) -> dict:
    resp = _client().parse(document=pdf_path, model=ADE_MODEL)
    return {
        "markdown": getattr(resp, "markdown", None),
        "chunks":   to_jsonable(getattr(resp, "chunks", None)),
        "splits":   to_jsonable(getattr(resp, "splits", None)),
        "metadata": to_jsonable(getattr(resp, "metadata", None)),
        "source_file": pdf_path.name,
        "model": ADE_MODEL,
    }

def _tables_from_markdown(md_text: str) -> List[pd.DataFrame]:
    if not md_text:
        return []
    # Convert markdown to HTML so pandas can read tables
    html = mdlib.markdown(md_text) if mdlib else md_text
    try:
        return [t for t in pd.read_html(io.StringIO(html)) if not t.empty]
    except Exception:
        return []

def _tables_from_chunks(chunks: list) -> List[pd.DataFrame]:
    out: List[pd.DataFrame] = []
    if not chunks:
        return out
    for ch in chunks:
        if isinstance(ch, dict) and ch.get("type") == "table":
            out += _tables_from_markdown(ch.get("markdown", ""))
    return out

def extract_cases_df(parsed: dict) -> pd.DataFrame:
    """
    Take the ADE dict (with 'chunks' and optional 'markdown') and build a single DataFrame
    from all tables we can find. Then do a light column harmonization.
    """
    frames: List[pd.DataFrame] = []
    frames += _tables_from_chunks(parsed.get("chunks"))
    if not frames and parsed.get("markdown"):
        frames += _tables_from_markdown(parsed["markdown"])
    if not frames:
        return pd.DataFrame()

    raw = pd.concat(frames, ignore_index=True)
    raw.columns = [str(c).strip() for c in raw.columns]

    # Column harmonization (keep raw address names; map to a common set)
    wanted = {
        "Case Type": "Case Type",
        "Case Number": "Case Number",
        "Case #": "Case Number",
        "Case Status": "Case Status",
        "Code Status": "Case Status",
        "Main Address": "Main Address",
        "Address": "Main Address",
        "Project": "Project",
        "District": "District",
        "Parcel": "Parcel",
        "Assigned To": "Assigned To",
        "Opened Date": "Opened Date",
        "Open Date": "Opened Date",
        "Closed Date": "Closed Date",
        "Closed": "Closed Date",
        # Extended fields commonly present in Oakland/Boca tables
        "Violation": "Violation",
        "Violation Status": "Violation Status",
        "Citation Issued": "Citation Issued",
        "Compliance Date": "Compliance Date",
        "Resolved Date": "Resolved Date",
        "Violation Fee Total": "Violation Fee Total",
        "Description": "Description",
    }
    cols = {c: next((v for k, v in wanted.items() if k.lower() == c.lower()), None) for c in raw.columns}
    cols = {k: v for k, v in cols.items() if v}
    df = raw.rename(columns=cols)
    keep = list(dict.fromkeys(wanted.values()))
    df = df[[c for c in keep if c in df.columns]].copy()

    # remove header-like rows
    if "Case Type" in df.columns:
        df = df[~df["Case Type"].astype(str).str.contains("Case Type", case=False, na=False)]

    # basic date coercion (won't fail if missing)
    for d in ("Opened Date", "Closed Date", "Compliance Date", "Resolved Date", "Citation Issued"):
        if d in df.columns:
            df[d] = pd.to_datetime(df[d], errors="coerce")

    # carry through source_file if present
    if parsed.get("source_file"):
        df["source_file"] = parsed["source_file"]
    return df.reset_index(drop=True)

# ---------- Batch runners ----------

def parse_batch_to_csv_city(items: Iterable[Tuple[str, Path]], out_name: str = "ade_latest.csv") -> pd.DataFrame:
    """
    items: iterable of (city, pdf_path)
    Saves raw JSON per file (using parse_pdf in the notebook loop) and accumulates a CSV.
    """
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    frames: List[pd.DataFrame] = []

    for city, p in items:
        try:
            parsed = parse_pdf(p)  # <-- removed extraneous args
            df = extract_cases_df(parsed)
            if not df.empty:
                df["city"] = city
                df["source_file"] = p.name
                frames.append(df)
        except Exception as e:
            print(f"[WARN] {city} :: {p.name}: {e}")

    if not frames:
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    csv_path = INTERIM_DIR / out_name
    csv_path.write_text(out.to_csv(index=False), encoding="utf-8")
    return out
