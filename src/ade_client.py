#for sdk wrapper and table extraction
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import io
import pandas as pd
from landingai_ade import LandingAIADE
from .config import ADE_API_KEY, ADE_MODEL, INTERIM_DIR

try:
    import markdown as mdlib
except Exception:
    mdlib = None

def _client() -> LandingAIADE:
    if not ADE_API_KEY:
        raise RuntimeError("VISION_AGENT_API_KEY not set in .env")
    return LandingAIADE(apikey=ADE_API_KEY)

def parse_pdf(pdf_path: Path) -> dict:
    resp = _client().parse(document=pdf_path, model=ADE_MODEL)
    return {"markdown": getattr(resp, "markdown", None),
            "chunks":   getattr(resp, "chunks", None),
            "source":   pdf_path.name}

def _tables_from_markdown(md_text: str) -> List[pd.DataFrame]:
    if not md_text:
        return []
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
            out += _tables_from_markdown(ch.get("markdown",""))
    return out

def extract_cases_df(parsed: dict) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    frames += _tables_from_chunks(parsed.get("chunks"))
    if not frames and parsed.get("markdown"):
        frames += _tables_from_markdown(parsed["markdown"])
    if not frames:
        return pd.DataFrame()
    raw = pd.concat(frames, ignore_index=True)
    raw.columns = [str(c).strip() for c in raw.columns]

    wanted = {
        "Case Type":"Case Type","Case Number":"Case Number","Case #":"Case Number",
        "Case Status":"Case Status","Code Status":"Case Status",
        "Main Address":"Main Address","Address":"Main Address",
        "Project":"Project","District":"District","Parcel":"Parcel",
        "Assigned To":"Assigned To","Opened Date":"Opened Date","Open Date":"Opened Date",
        "Closed Date":"Closed Date","Closed":"Closed Date",
    }
    cols = {c: next((v for k,v in wanted.items() if k.lower()==c.lower()), None) for c in raw.columns}
    cols = {k:v for k,v in cols.items() if v}
    df = raw.rename(columns=cols)
    keep = list(dict.fromkeys(wanted.values()))
    df = df[[c for c in keep if c in df.columns]].copy()
    # drop header-like rows
    if "Case Type" in df:
        df = df[~df["Case Type"].astype(str).str.contains("Case Type", case=False, na=False)]
    for d in ("Opened Date","Closed Date"):
        if d in df: df[d] = pd.to_datetime(df[d], errors="coerce")
    if parsed.get("source"):
        df["source_file"] = parsed["source"]
    return df.reset_index(drop=True)

def parse_batch_to_csv(pdf_paths: Iterable[Path], out_name="ade_latest.csv") -> pd.DataFrame:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for p in pdf_paths:
        try:
            r  = parse_pdf(p)
            df = extract_cases_df(r)
            if not df.empty:
                df["source_file"] = p.name
                frames.append(df)
        except Exception as e:
            print(f"[WARN] {p.name}: {e}")
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    (INTERIM_DIR / out_name).write_text(out.to_csv(index=False), encoding="utf-8")
    return out
