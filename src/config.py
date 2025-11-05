from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR     = ROOT / "input_folder"
RESULTS_DIR   = ROOT / "results_folder"
INTERIM_DIR   = ROOT / "results_folder" / "interim"

ADE_API_KEY = os.getenv("VISION_AGENT_API_KEY")
ADE_MODEL   = os.getenv("ADE_MODEL", "dpt-2")
MASTER_PARQUET = RESULTS_DIR / "violations_master.parquet"
MASTER_CSV     = RESULTS_DIR / "violations_master.csv"
