# ✅ **README.md**

# Coderisk-SF

**Automated Extraction, Normalization, and Analysis of Code Violation Reports Using LandingAI ADE**

This project provides an end-to-end pipeline for extracting structured data from code-enforcement PDF reports across multiple South Florida cities. It uses **LandingAI’s Agentic Document Extraction (ADE)** to parse heterogeneous documents, apply city-specific schemas, normalize the outputs into a unified structure, and store the results for further risk analysis and reporting.

---

## 1. Project Purpose

Many cities publish code-violation data as PDF reports with inconsistent formatting, table layouts, and field names.
This project automates the entire workflow:

1. **Extract** PDF data using LandingAI ADE
2. **Parse tables and metadata** into structured DataFrames
3. **Apply city-specific normalization rules**
4. **Unify all cities into a consolidated master dataset**
5. **Store results for risk analysis (CSV + Parquet)**
6. **Preserve raw JSON output for traceability and audits**

This enables scalable analytics such as:

* Most frequent violation types
* Geographic risk patterns
* Repeated offenders
* Time-to-closure metrics
* City-to-city comparisons

---

## 2. Project Structure

```
coderisk-sf/
│
├── input_folder/                 # Raw PDFs grouped by city
│   ├── oaklandpark/
│   ├── bocaraton/
│   ├── pompano/
│   └── wiltonmanor/
│
├── results_folder/               # Extraction outputs
│   ├── oaklandpark/
│   │   ├── raw_json/             # Raw ADE JSON output
│   │   └── tables/               # CSV and Parquet tables per PDF
│   ├── bocaraton/
│   │   ├── raw_json/
│   │   └── tables/
│   ├── pompano/
│   │   ├── raw_json/
│   │   └── tables/
│   └── wiltonmanor/
│       ├── raw_json/
│       └── tables/
│
├── src/
│   ├── ade_client.py             # ADE parsing and table extraction
│   ├── normalizers.py            # City-level and global normalization
│   ├── db.py                     # Optional SQLite utilities
│   ├── utils.py                  # Helper functions
│   ├── config.py                 # API key + model configuration
│   └── ade_work.ipynb            # Main Jupyter workflow
│
├── requirements.txt
└── .env.example                  # Example environment configuration
```

---

## 3. Environment Setup

### Create and activate a virtual environment

```
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows
```

### Install dependencies

```
pip install -r requirements.txt
```

### Configure environment variables

Rename `.env.example` to `.env` and set:

```
VISION_AGENT_API_KEY=your-landingai-key
ADE_MODEL=dpt-2
```

---

## 4. Folder Initialization

Before running extraction, create the expected output structure:

```
mkdir -p input_folder/oaklandpark
mkdir -p input_folder/bocaraton
mkdir -p input_folder/pompano
mkdir -p input_folder/wiltonmanor

mkdir -p results_folder/oaklandpark/raw_json
mkdir -p results_folder/oaklandpark/tables
mkdir -p results_folder/bocaraton/raw_json
mkdir -p results_folder/bocaraton/tables
mkdir -p results_folder/pompano/raw_json
mkdir -p results_folder/pompano/tables
mkdir -p results_folder/wiltonmanor/raw_json
mkdir -p results_folder/wiltonmanor/tables
```

Place your PDFs in the corresponding city folders.

---

## 5. Running the Extraction (ADE)

The workflow is driven from:

```
src/ade_work.ipynb
```

The notebook performs:

1. Environment and path setup
2. Initialization of the LandingAI ADE client
3. Directory scanning and validation
4. PDF parsing using `.parse()`
5. Saving raw JSON outputs
6. Parsing tables into pandas DataFrames
7. Saving normalized tables per PDF

---

## 6. Normalization Layer

Each city uses different column names and formats.
The normalization layer performs:

* Column standardization
* Date parsing (open/close dates)
* Standard field alignment (Case Number, Case Type, Status, Address, Parcel, Assigned To, etc.)
* City tagging
* Output validation

This enables merging all cities into a unified master dataset for analytics.

---

## 7. Output Formats

Each PDF produces:

* `raw_json/*.json` — full ADE JSON output
* `tables/*.csv` — extracted table
* `tables/*.parquet` — column-preserving version for analytics

---

## 8. Future Enhancements

The project is designed to support future extensions:

* Automatic schema inference
* Retrieval-augmented enrichment (zip code lookup, geocoding, census data)
* Trend forecasting
* Risk scoring models
* API endpoints for real-time queries

---

## 9. Requirements

Python 3.10+
LandingAI ADE SDK
pandas
markdown
pyarrow
Jupyter Notebook

---

## 10. License

This project is developed for the LandingAI Financial Hack NYC.