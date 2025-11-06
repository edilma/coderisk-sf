from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR   = ROOT / "input_folder"
RESULTS_DIR = ROOT / "results_folder"
RAW_JSON_DIR = RESULTS_DIR / "raw_json"            # <- for raw ADE JSON
INTERIM_DIR = RESULTS_DIR / "extracted_tables"     # <- your CSV/parquet dumps

ADE_API_KEY = os.getenv("ADE_API_KEY") or os.getenv("VISION_AGENT_API_KEY")
ADE_MODEL   = os.getenv("ADE_MODEL", "dpt-2")
